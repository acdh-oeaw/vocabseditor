import datetime
import time

from browsing.utils import BaseCreateView, BaseUpdateView, GenericListView
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from guardian.shortcuts import get_objects_for_user
from reversion.models import Version

from vocabs.filters import (
    SkosCollectionListFilter,
    SkosConceptListFilter,
    SkosConceptSchemeListFilter,
)
from vocabs.forms import (
    CollectionLabelFormSet,
    CollectionNoteFormSet,
    CollectionSourceFormSet,
    ConceptLabelFormSet,
    ConceptNoteFormSet,
    ConceptSchemeDescriptionFormSet,
    ConceptSchemeSourceFormSet,
    ConceptSchemeTitleFormSet,
    ConceptSourceFormSet,
    SkosCollectionForm,
    SkosCollectionFormHelper,
    SkosConceptForm,
    SkosConceptFormHelper,
    SkosConceptSchemeForm,
    SkosConceptSchemeFormHelper,
)
from vocabs.models import SkosCollection, SkosConcept, SkosConceptScheme
from vocabs.rdf_utils import RDF_FORMATS, graph_construct_qs
from vocabs.tables import SkosCollectionTable, SkosConceptSchemeTable, SkosConceptTable
from vocabs.utils import delete_legacy_ids, delete_skos_notations


class BaseDetailView(DetailView):
    def get_queryset(self, **kwargs):
        qs = get_objects_for_user(
            self.request.user,
            perms=[
                "view_{}".format(self.model.__name__.lower()),
                "change_{}".format(self.model.__name__.lower()),
                "delete_{}".format(self.model.__name__.lower()),
            ],
            klass=self.model,
        )
        return qs

    def get_context_data(self, **kwargs):
        context = super(BaseDetailView, self).get_context_data(**kwargs)
        context["history"] = Version.objects.get_for_object(self.object)
        return context


class BaseDeleteView(DeleteView):
    def get_queryset(self, **kwargs):
        qs = get_objects_for_user(
            self.request.user,
            perms=[
                "view_{}".format(self.model.__name__.lower()),
                "change_{}".format(self.model.__name__.lower()),
                "delete_{}".format(self.model.__name__.lower()),
            ],
            klass=self.model,
        )
        return qs


######################################################################
#
# SkosConceptScheme
#
######################################################################


class SkosConceptSchemeListView(GenericListView):
    model = SkosConceptScheme
    table_class = SkosConceptSchemeTable
    filter_class = SkosConceptSchemeListFilter
    formhelper_class = SkosConceptSchemeFormHelper
    init_columns = [
        "id",
        "title",
    ]


class SkosConceptSchemeDetailView(BaseDetailView):
    model = SkosConceptScheme
    template_name = "vocabs/skosconceptscheme_detail.html"

    def get_context_data(self, **kwargs):
        context = super(SkosConceptSchemeDetailView, self).get_context_data(**kwargs)
        context["concepts"] = SkosConcept.objects.filter(scheme=self.kwargs.get("pk"))
        return context


@login_required
def delete_legacy_id_view(request, pk):
    obj = get_object_or_404(SkosConceptScheme, pk=pk)
    delete_legacy_ids(obj)
    return redirect(obj)


@login_required
def delete_notation_view(request, pk):
    obj = get_object_or_404(SkosConceptScheme, pk=pk)
    delete_skos_notations(obj)
    return redirect(obj)


class SkosConceptSchemeCreate(BaseCreateView):
    model = SkosConceptScheme
    form_class = SkosConceptSchemeForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(SkosConceptSchemeCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data["titles"] = ConceptSchemeTitleFormSet(self.request.POST)
            data["descriptions"] = ConceptSchemeDescriptionFormSet(self.request.POST)
            data["sources"] = ConceptSchemeSourceFormSet(self.request.POST)
        else:
            data["titles"] = ConceptSchemeTitleFormSet()
            data["descriptions"] = ConceptSchemeDescriptionFormSet()
            data["sources"] = ConceptSchemeSourceFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        titles = context["titles"]
        descriptions = context["descriptions"]
        sources = context["sources"]
        with transaction.atomic():
            form.instance.created_by = self.request.user
            # cs should be saved first because fk object are related to it
            self.object = form.save(commit=False)
            if titles.is_valid():
                titles.instance = self.object
                titles.save(commit=False)
            else:
                return super(SkosConceptSchemeCreate, self).form_invalid(form)
            if descriptions.is_valid():
                descriptions.instance = self.object
                descriptions.save(commit=False)
            else:
                return super(SkosConceptSchemeCreate, self).form_invalid(form)
            if sources.is_valid():
                sources.instance = self.object
                sources.save(commit=False)
            else:
                return super(SkosConceptSchemeCreate, self).form_invalid(form)
            self.object = form.save()
            titles.save()
            descriptions.save()
            sources.save()

        return super(SkosConceptSchemeCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "vocabs:skosconceptscheme_detail", kwargs={"pk": self.object.pk}
        )

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptSchemeCreate, self).dispatch(*args, **kwargs)


class SkosConceptSchemeUpdate(BaseUpdateView):
    model = SkosConceptScheme
    form_class = SkosConceptSchemeForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(SkosConceptSchemeUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data["titles"] = ConceptSchemeTitleFormSet(
                self.request.POST, instance=self.object
            )
            data["descriptions"] = ConceptSchemeDescriptionFormSet(
                self.request.POST, instance=self.object
            )
            data["sources"] = ConceptSchemeSourceFormSet(
                self.request.POST, instance=self.object
            )
        else:
            data["titles"] = ConceptSchemeTitleFormSet(instance=self.object)
            data["descriptions"] = ConceptSchemeDescriptionFormSet(instance=self.object)
            data["sources"] = ConceptSchemeSourceFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        titles = context["titles"]
        descriptions = context["descriptions"]
        sources = context["sources"]
        with transaction.atomic():
            if titles.is_valid():
                titles.instance = self.object
                titles.save()
            else:
                # raise forms.ValidationError("Both fields should be filled")
                return super(SkosConceptSchemeUpdate, self).form_invalid(form)
            if descriptions.is_valid():
                descriptions.instance = self.object
                descriptions.save()
            else:
                return super(SkosConceptSchemeUpdate, self).form_invalid(form)
            if sources.is_valid():
                sources.instance = self.object
                sources.save()
            else:
                return super(SkosConceptSchemeUpdate, self).form_invalid(form)
        return super(SkosConceptSchemeUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "vocabs:skosconceptscheme_detail", kwargs={"pk": self.object.pk}
        )

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptSchemeUpdate, self).dispatch(*args, **kwargs)


class SkosConceptSchemeDelete(BaseDeleteView):
    model = SkosConceptScheme
    template_name = "webpage/confirm_delete.html"
    success_url = reverse_lazy("vocabs:browse_schemes")

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptSchemeDelete, self).dispatch(*args, **kwargs)


######################################################################
#
# SkosCollection
#
######################################################################


class SkosCollectionListView(GenericListView):
    model = SkosCollection
    table_class = SkosCollectionTable
    filter_class = SkosCollectionListFilter
    formhelper_class = SkosCollectionFormHelper
    init_columns = [
        "id",
        "name",
        "scheme",
    ]


class SkosCollectionDetailView(BaseDetailView):
    model = SkosCollection
    template_name = "vocabs/skoscollection_detail.html"


class SkosCollectionCreate(BaseCreateView):
    model = SkosCollection
    form_class = SkosCollectionForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(SkosCollectionCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data["labels"] = CollectionLabelFormSet(self.request.POST)
            data["notes"] = CollectionNoteFormSet(self.request.POST)
            data["sources"] = CollectionSourceFormSet(self.request.POST)
        else:
            data["labels"] = CollectionLabelFormSet()
            data["notes"] = CollectionNoteFormSet()
            data["sources"] = CollectionSourceFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        labels = context["labels"]
        notes = context["notes"]
        sources = context["sources"]
        with transaction.atomic():
            form.instance.created_by = self.request.user
            self.object = form.save(commit=False)
            if labels.is_valid():
                labels.instance = self.object
                labels.save(commit=False)
            else:
                return super(SkosCollectionCreate, self).form_invalid(form)
            if notes.is_valid():
                notes.instance = self.object
                notes.save(commit=False)
            else:
                return super(SkosCollectionCreate, self).form_invalid(form)
            if sources.is_valid():
                sources.instance = self.object
                sources.save(commit=False)
            else:
                return super(SkosCollectionCreate, self).form_invalid(form)
            self.object = form.save()
            labels.save()
            notes.save()
            sources.save()
        return super(SkosCollectionCreate, self).form_valid(form)

    def get_initial(self):
        initial = super(SkosCollectionCreate, self).get_initial()
        if self.request.GET.get("scheme"):
            initial["scheme"] = SkosConceptScheme.objects.get(
                pk=self.request.GET.get("scheme")
            )
        return initial

    def get_success_url(self):
        return reverse_lazy(
            "vocabs:skoscollection_detail", kwargs={"pk": self.object.pk}
        )

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosCollectionCreate, self).dispatch(*args, **kwargs)


class SkosCollectionUpdate(BaseUpdateView):
    model = SkosCollection
    form_class = SkosCollectionForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(SkosCollectionUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data["labels"] = CollectionLabelFormSet(
                self.request.POST, instance=self.object
            )
            data["notes"] = CollectionNoteFormSet(
                self.request.POST, instance=self.object
            )
            data["sources"] = CollectionSourceFormSet(
                self.request.POST, instance=self.object
            )
        else:
            data["labels"] = CollectionLabelFormSet(instance=self.object)
            data["notes"] = CollectionNoteFormSet(instance=self.object)
            data["sources"] = CollectionSourceFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        labels = context["labels"]
        notes = context["notes"]
        sources = context["sources"]
        with transaction.atomic():
            if labels.is_valid():
                labels.instance = self.object
                labels.save()
            else:
                return super(SkosCollectionUpdate, self).form_invalid(form)
            if notes.is_valid():
                notes.instance = self.object
                notes.save()
            else:
                return super(SkosCollectionUpdate, self).form_invalid(form)
            if sources.is_valid():
                sources.instance = self.object
                sources.save()
            else:
                return super(SkosCollectionUpdate, self).form_invalid(form)
        return super(SkosCollectionUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "vocabs:skoscollection_detail", kwargs={"pk": self.object.pk}
        )

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosCollectionUpdate, self).dispatch(*args, **kwargs)


class SkosCollectionDelete(BaseDeleteView):
    model = SkosCollection
    template_name = "webpage/confirm_delete.html"
    success_url = reverse_lazy("vocabs:browse_skoscollections")

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosCollectionDelete, self).dispatch(*args, **kwargs)


######################################################################
#
# SkosConcept
#
######################################################################


class SkosConceptListView(GenericListView):
    model = SkosConcept
    table_class = SkosConceptTable
    filter_class = SkosConceptListFilter
    formhelper_class = SkosConceptFormHelper
    init_columns = [
        "id",
        "pref_label",
        "scheme",
    ]

    def get_queryset(self, **kwargs):
        qs = super(SkosConceptListView, self).get_queryset()
        return qs.order_by("id")


class SkosConceptDetailView(BaseDetailView):
    model = SkosConcept
    template_name = "vocabs/skosconcept_detail.html"
    success_url = None

    def get_context_data(self, **kwargs):
        context = super(SkosConceptDetailView, self).get_context_data(**kwargs)
        return context


class SkosConceptCreate(BaseCreateView):
    model = SkosConcept
    form_class = SkosConceptForm

    def get_context_data(self, **kwargs):
        data = super(SkosConceptCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data["labels"] = ConceptLabelFormSet(self.request.POST)
            data["notes"] = ConceptNoteFormSet(self.request.POST)
            data["sources"] = ConceptSourceFormSet(self.request.POST)
        else:
            data["labels"] = ConceptLabelFormSet()
            data["notes"] = ConceptNoteFormSet()
            data["sources"] = ConceptSourceFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        labels = context["labels"]
        notes = context["notes"]
        sources = context["sources"]
        with transaction.atomic():
            form.instance.created_by = self.request.user
            self.object = form.save(commit=False)
            if labels.is_valid():
                labels.instance = self.object
                labels.save(commit=False)
            else:
                return super(SkosConceptCreate, self).form_invalid(form)
            if notes.is_valid():
                notes.instance = self.object
                notes.save(commit=False)
            else:
                return super(SkosConceptCreate, self).form_invalid(form)
            if sources.is_valid():
                sources.instance = self.object
                sources.save(commit=False)
            else:
                return super(SkosConceptCreate, self).form_invalid(form)
            self.object = form.save()
            labels.save()
            notes.save()
            sources.save()
        return super(SkosConceptCreate, self).form_valid(form)

    def get_initial(self):
        initial = super(SkosConceptCreate, self).get_initial()
        if self.request.GET.get("scheme"):
            initial["scheme"] = SkosConceptScheme.objects.get(
                pk=self.request.GET.get("scheme")
            )
        if self.request.GET.get("collection"):
            initial["collection"] = SkosCollection.objects.get(
                pk=self.request.GET.get("collection")
            )
        return initial

    def get_success_url(self):
        return reverse_lazy("vocabs:skosconcept_detail", kwargs={"pk": self.object.pk})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptCreate, self).dispatch(*args, **kwargs)


class SkosConceptUpdate(BaseUpdateView):
    model = SkosConcept
    form_class = SkosConceptForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(SkosConceptUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data["labels"] = ConceptLabelFormSet(
                self.request.POST, instance=self.object
            )
            data["notes"] = ConceptNoteFormSet(self.request.POST, instance=self.object)
            data["sources"] = ConceptSourceFormSet(
                self.request.POST, instance=self.object
            )
        else:
            data["labels"] = ConceptLabelFormSet(instance=self.object)
            data["notes"] = ConceptNoteFormSet(instance=self.object)
            data["sources"] = ConceptSourceFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        labels = context["labels"]
        notes = context["notes"]
        sources = context["sources"]
        with transaction.atomic():
            if labels.is_valid():
                labels.instance = self.object
                labels.save()
            else:
                return super(SkosConceptUpdate, self).form_invalid(form)
            if notes.is_valid():
                notes.instance = self.object
                notes.save()
            else:
                return super(SkosConceptUpdate, self).form_invalid(form)
            if sources.is_valid():
                sources.instance = self.object
                sources.save()
            else:
                return super(SkosConceptUpdate, self).form_invalid(form)
        return super(SkosConceptUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy("vocabs:skosconcept_detail", kwargs={"pk": self.object.pk})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptUpdate, self).dispatch(*args, **kwargs)


class SkosConceptDelete(BaseDeleteView):
    model = SkosConcept
    template_name = "webpage/confirm_delete.html"
    success_url = reverse_lazy("vocabs:browse_vocabs")

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SkosConceptDelete, self).dispatch(*args, **kwargs)


###################################################
# SkosConcepts download as one ConceptScheme
###################################################


class SkosConceptDL(GenericListView):
    model = SkosConcept
    table_class = SkosConceptTable
    filter_class = SkosConceptListFilter
    formhelper_class = SkosConceptFormHelper

    def render_to_response(self, context):
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime(
            "%Y-%m-%d-%H-%M-%S"
        )
        response = HttpResponse(content_type="application/xml; charset=utf-8")
        filename = "download_{}".format(timestamp)
        get_format = self.request.GET.get("format", default="pretty-xml")
        qs = self.get_queryset()
        response["Content-Disposition"] = (
            f'attachment; filename="{filename}.{RDF_FORMATS[get_format]}"'
        )
        g = graph_construct_qs(qs)
        g.serialize(destination=response, format=get_format)
        return response
