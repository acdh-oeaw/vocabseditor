from dal import autocomplete
from .models import SkosConcept, SkosConceptScheme, SkosCollection
from guardian.shortcuts import get_objects_for_user
from django.contrib.auth.models import User
from mptt.settings import DEFAULT_LEVEL_INDICATOR


class SkosConceptAC(autocomplete.Select2QuerySetView):

    def get_result_label(self, item):
        level_indicator = DEFAULT_LEVEL_INDICATOR * item.level
        return level_indicator + ' ' + str(item)

    def get_queryset(self):
        qs = get_objects_for_user(self.request.user,
            'view_skosconcept',
            klass=SkosConcept)
        scheme = self.forwarded.get('scheme', None)
        if scheme:
            qs = qs.filter(scheme=scheme)
        if self.q:
            qs = qs.filter(pref_label__icontains=self.q)
        return qs


class SkosConceptExternalMatchAC(autocomplete.Select2QuerySetView):

    def get_result_label(self, item):
        level_indicator = DEFAULT_LEVEL_INDICATOR * item.level
        return level_indicator + ' ' + str(item)

    def get_queryset(self):
        qs = get_objects_for_user(self.request.user,
            'view_skosconcept',
            klass=SkosConcept)
        scheme = self.forwarded.get('scheme', None)
        if scheme:
            qs = qs.exclude(scheme=scheme)
        if self.q:
            qs = qs.filter(pref_label__icontains=self.q)
        return qs


class SkosConceptSchemeAC(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = get_objects_for_user(self.request.user,
            'view_skosconceptscheme',
            klass=SkosConceptScheme)
        if self.q:
            qs = qs.filter(title__icontains=self.q)

        return qs


class SkosCollectionAC(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = get_objects_for_user(self.request.user,
            'view_skoscollection',
            klass=SkosCollection)
        scheme = self.forwarded.get('scheme', None)
        if scheme:
            qs = qs.filter(scheme=scheme)

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class UserAC(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = User.objects.exclude(username=self.request.user)
        if self.q:
            qs = qs.filter(username__icontains=self.q)

        return qs
