from dal import autocomplete
from .models import SkosLabel, SkosConcept, SkosConceptScheme, SkosCollection
from django.db.models import Q


class SpecificConcepts(autocomplete.Select2QuerySetView):

    def get_result_label(self, item):
        return "{}".format(item.label)

    def get_queryset(self):
        try:
            scheme = self.kwargs['scheme']
            selected_scheme = SkosConceptScheme.objects.filter(dc_title__icontains=scheme)
        except KeyError:
            selected_scheme = None
        if selected_scheme:
            qs = SkosConcept.objects.filter(scheme__in=selected_scheme)
        else:
            qs = SkosConcept.objects.all()

        if self.q:
            direct_match = qs.filter(pref_label__icontains=self.q)
            plus_narrower = direct_match | qs.filter(broader_concept__in=direct_match)
            return plus_narrower

        return []


class SKOSConstraintACNoHierarchy(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        scheme = self.request.GET.get('scheme')
        try:
            selected_scheme = SkosConceptScheme.objects.get(dc_title=scheme)
            qs = SkosConcept.objects.filter(scheme=selected_scheme)
        except:
            qs = SkosConcept.objects.all()

        if self.q:
            qs = qs.filter(
                Q(pref_label__icontains=self.q)
            )

        return qs


class SKOSConstraintAC(autocomplete.Select2QuerySetView):
    def get_result_label(self, item):
        if len(item.skos_broader.all()) > 0:
            return "{} >> {}".format(item.skos_broader.all()[0], item.pref_label)
        else:
            return "{}".format(item.pref_label)

    def get_queryset(self):
        scheme = self.request.GET.get('scheme')
        try:
            selected_scheme = SkosConceptScheme.objects.get(dc_title=scheme)
            qs = SkosConcept.objects.filter(scheme=selected_scheme)
        except:
            qs = SkosConcept.objects.all()

        if self.q:
            direct_match = qs.filter(pref_label__icontains=self.q)
            plus_narrower = direct_match | qs.filter(broader_concept__in=direct_match)
            return plus_narrower
        else:
            return qs


class SkosLabelAC(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = SkosLabel.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class SkosConceptAC(autocomplete.Select2QuerySetView):

    def get_result_label(self, item):
        return "{}".format(item.label)

    def get_queryset(self):
        qs = SkosConcept.objects.all()
        if self.q:
            direct_match = qs.filter(pref_label__icontains=self.q)
            plus_narrower = qs.filter(broader_concept__in=direct_match) | direct_match
            return plus_narrower
        else:
            return qs


class SkosConceptPrefLabalAC(autocomplete.Select2ListView):

    def get_list(self):
        concepts = SkosConcept.objects.filter(pref_label__icontains=self.q)
        pref_labels = set([x.pref_label for x in concepts])
        return pref_labels


class SkosConceptSchemeAC(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = SkosConceptScheme.objects.all()

        if self.q:
            qs = qs.filter(dc_title__icontains=self.q)

        return qs


class SkosCollectionAC(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = SkosCollection.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs
