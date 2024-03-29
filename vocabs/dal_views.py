import requests
import json

from dal import autocomplete
from .models import SkosConcept, SkosConceptScheme, SkosCollection
from guardian.shortcuts import get_objects_for_user
from django.contrib.auth.models import User
from mptt.settings import DEFAULT_LEVEL_INDICATOR
from .endpoints import ENDPOINT, DbpediaAC


################ Global autocomplete for external concepts ################


def global_autocomplete(request, endpoint):
    choices = []
    q = request.GET.get('q')
    headers = {'accept': 'application/json'}
    ac_instance = ENDPOINT.get(endpoint, DbpediaAC())
    if ac_instance.__class__.__name__.startswith('Fish'):
        scheme = ac_instance.scheme_dict.get(endpoint, 'FISH Event Types Thesaurus')
        r = requests.get(ac_instance.get_url(), headers=headers,
                         params=ac_instance.payload(scheme=scheme, q=q))
    else:
        r = requests.get(ac_instance.get_url(), headers=headers,
                         params=ac_instance.payload(q=q))
    response = json.loads(r.content.decode('utf-8'))
    choices = ac_instance.parse_response(response=response)
    return choices


###########################################################################


class ExternalLinkAC(autocomplete.Select2ListView):

    def get_list(self):
        endpoint = self.forwarded.get('endpoint', None)
        global_ac = global_autocomplete(self.request, endpoint=endpoint)
        return global_ac


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
