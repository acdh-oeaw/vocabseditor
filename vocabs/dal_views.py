from dal import autocomplete
from .models import SkosConcept, SkosConceptScheme, SkosCollection
from guardian.shortcuts import get_objects_for_user
from django.contrib.auth.models import User
from mptt.settings import DEFAULT_LEVEL_INDICATOR
import requests, json
from django import http
from django.utils import six
from .endpoints import *

################ Global autocomplete for external concepts ################


def global_autocomplete(request, endpoint):
    choices = []
    q = request.GET.get('q')
    headers = {'accept': 'application/json'}
    ac_instance = None
    if endpoint == ENDPOINTS[0][0]:
        ac_instance = DbpediaAC()        
    elif endpoint == ENDPOINTS[1][0]:
        ac_instance = GndAC()
    elif endpoint == ENDPOINTS[2][0]:
        ac_instance = GemetAC()
    elif endpoint == ENDPOINTS[3][0]:
        ac_instance = FishAC()        
    else:
        return choices
    r = requests.get(ac_instance.get_url()+q, headers=headers)
    response = json.loads(r.content.decode('utf-8'))
    choices = ac_instance.parse_response(response=response)
    return choices
    

###########################################################################


class ExternalLinkAC(autocomplete.Select2ListView):

    def get_list(self):
        choices = []
        endpoint = self.forwarded.get('endpoint', None)
        print(endpoint)
        global_ac = global_autocomplete(self.request, endpoint=endpoint)
        return global_ac
        # self.forwarded = json.loads(
        #         getattr(self.request, self.request.method).get('endpoint', '{}')
        #     )
        #endpoint = self.request.GET.get('endpoint')
        
        # headers = {'accept': 'application/json'}
        # if endpoint == 'http://lookup.dbpedia.org/api/search/PrefixSearch?QueryString=':
        #     q = self.request.GET.get('q')
        #     r = requests.get(endpoint+q, headers=headers)
        #     response = json.loads(r.content.decode('utf-8'))
        #     for x in response['results']:
        #     # item = {x['uri']: x['label']}
        #     # choices.append(item)
        #         choices.append(str(x['uri'])+' - '+str(x['label']))
        # elif endpoint == 'https://lobid.org/gnd/search?q=':
        #     q = self.request.GET.get('q')
        #     r = requests.get(endpoint+q+'&format=json:preferredName', headers=headers)
        #     response = json.loads(r.content.decode('utf-8'))
        #     for x in response:
        #     # item = {x['uri']: x['label']}
        #     # choices.append(item)
        #         choices.append(str(x['id'])+' - '+str(x['label']))
        # elif endpoint == 'https://www.heritagedata.org/live/services/getConceptLabelMatch?schemeURI=http://purl.org/heritagedata/schemes/560&contains=':
        #     q = self.request.GET.get('q')
        #     r = requests.get(endpoint+q, headers=headers)
        #     response = json.loads(r.content.decode('utf-8'))
        #     for x in response:
        #     # item = {x['uri']: x['label']}
        #     # choices.append(item)
        #         choices.append(str(x['uri'])+' - '+str(x['label']))
        # elif endpoint == 'https://www.eionet.europa.eu/gemet/getConceptsMatchingKeyword?&search_mode=4&keyword=':
        #     q = self.request.GET.get('q')
        #     r = requests.get(endpoint+q, headers=headers)
        #     response = json.loads(r.content.decode('utf-8'))
        #     for x in response:
        #     # item = {x['uri']: x['label']}
        #     # choices.append(item)
        #         choices.append(str(x['uri'])+' - '+str(x['preferredLabel']['string'])+'@'+str(x['preferredLabel']['language']))
        # else:
        #     pass
        # return choices

        # global_list = global_autocomplete(self.request)
        # return global_list


    def results(self, results):
        """Return the result dictionary."""
        return [dict(id=x, text=x) for x in results]
        #return [str(x) for x in results]

    def autocomplete_results(self, results):
        """Return list of strings that match the autocomplete query."""
        return [str(x) for x in results]

    def get(self, request, *args, **kwargs):
        """Return option list json response."""
        results = self.get_list()
        print(results)
        create_option = []
        if self.q:
            results = self.autocomplete_results(results)
            print(results)
            if hasattr(self, 'create'):
                create_option = [{
                    'id': self.q,
                    'text': 'Create "%s"' % self.q,
                    'create_id': True
                }]
        return http.JsonResponse({
            'results': self.results(results) + create_option
        }, content_type='application/json')


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
