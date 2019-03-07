from dal import autocomplete
from .models import SkosConcept, SkosConceptScheme, SkosCollection
from guardian.shortcuts import get_objects_for_user
from django.contrib.auth.models import User
from mptt.settings import DEFAULT_LEVEL_INDICATOR
import requests, json
from django import http
from django.utils import six

################ Global autocomplete for external concepts ################

dbpedia = 'dbpedia''http://lookup.dbpedia.org/api/search/PrefixSearch?QueryString='
gnd = 'https://lobid.org/gnd/search?q='
fish = 'https://www.heritagedata.org/live/services/getConceptLabelMatch?schemeURI=http://purl.org/heritagedata/schemes/560&contains='
gemet = 'http://www.eionet.europa.eu/gemet/getConceptsMatchingKeyword?&search_mode=0&keyword='


def global_autocomplete(request):
    choices = []
    q = request.GET.get('q')
    headers = {'accept': 'application/json'}
    ##### dbpedia api ######
    dbpedia_url = 'http://lookup.dbpedia.org/api/search/PrefixSearch?QueryString='
    dbpedia_url += q
    dbpedia_r = requests.get(dbpedia_url, headers=headers)
    dbpedia_response = json.loads(dbpedia_r.content.decode('utf-8'))
    for x in dbpedia_response['results']:
        # item = {x['uri']: x['label']}
        # choices.append(item)
        choices.append(str(x['uri'])+' - '+str(x['label']))
    ##### gnd api ######
    # gnd_url = 'https://lobid.org/gnd/search?q='
    # gnd_url += q
    # gnd_url += '&format=json:preferredName'
    # gnd_r = requests.get(gnd_url, headers=headers)
    # gnd_response = json.loads(gnd_r.content.decode('utf-8'))
    # for x in gnd_response:
    #     item = {x['id']: x['label']}
    #     choices.append(item)
        #choices.append(str(x['id'])+' - '+str(x['label']))
    ##### fish api ######
    fish_url = 'https://www.heritagedata.org/live/services/getConceptLabelMatch?schemeURI=http://purl.org/heritagedata/schemes/560&contains='
    fish_url += q
    #fish_url += '&format=json'
    fish_r = requests.get(fish_url, headers=headers)
    fish_response = json.loads(fish_r.content.decode('utf-8'))
    for x in fish_response:
        # item = {x['uri']: x['label']}
        # choices.append(item)
        choices.append(str(x['uri'])+' - '+str(x['label']))
    ##### gemet api ######
    gemet_url = 'http://www.eionet.europa.eu/gemet/getConceptsMatchingKeyword?&search_mode=0&keyword='
    gemet_url += q
    gemet_url += '&format=json'
    gemet_r = requests.get(gemet_url, headers=headers)
    gemet_response = json.loads(gemet_r.content.decode('utf-8'))
    for x in gemet_response:
        # item = {x['uri']: x['preferredLabel']}
        # choices.append(item)
        choices.append(str(x['uri'])+' - '+str(x['preferredLabel']['string'])+'@'+str(x['preferredLabel']['language']))
    return choices


###########################################################################


class ExternalLinkAC(autocomplete.Select2ListView):

    def get_list(self):
        # final = []
        # global_list = global_autocomplete(self.request)
        # for x in global_list:
        #     for key, value in x.items():
        #         new_item = {'id': key, 'label': value}
        #         #new_item = dict(id=x[key], label=x[value])
        #         final.append(new_item)
        # #print(final)

        # return final
        choices = []
        endpoint = self.forwarded.get('endpoint', None)
        print(endpoint)
        # self.forwarded = json.loads(
        #         getattr(self.request, self.request.method).get('endpoint', '{}')
        #     )
        #endpoint = self.request.GET.get('endpoint')
        
        headers = {'accept': 'application/json'}
        if endpoint == 'http://lookup.dbpedia.org/api/search/PrefixSearch?QueryString=':
            q = self.request.GET.get('q')
            r = requests.get(endpoint+q, headers=headers)
            response = json.loads(r.content.decode('utf-8'))
            for x in response['results']:
            # item = {x['uri']: x['label']}
            # choices.append(item)
                choices.append(str(x['uri'])+' - '+str(x['label']))
        elif endpoint == 'https://lobid.org/gnd/search?q=':
            q = self.request.GET.get('q')
            r = requests.get(endpoint+q+'&format=json:preferredName', headers=headers)
            response = json.loads(r.content.decode('utf-8'))
            for x in response:
            # item = {x['uri']: x['label']}
            # choices.append(item)
                choices.append(str(x['id'])+' - '+str(x['label']))
        elif endpoint == 'https://www.heritagedata.org/live/services/getConceptLabelMatch?schemeURI=http://purl.org/heritagedata/schemes/560&contains=':
            q = self.request.GET.get('q')
            r = requests.get(endpoint+q, headers=headers)
            response = json.loads(r.content.decode('utf-8'))
            for x in response:
            # item = {x['uri']: x['label']}
            # choices.append(item)
                choices.append(str(x['uri'])+' - '+str(x['label']))
        elif endpoint == 'http://www.eionet.europa.eu/gemet/getConceptsMatchingKeyword?&search_mode=0&keyword=':
            q = self.request.GET.get('q')
            r = requests.get(endpoint+q, headers=headers)
            response = json.loads(r.content.decode('utf-8'))
            for x in response:
            # item = {x['uri']: x['label']}
            # choices.append(item)
                choices.append(str(x['uri'])+' - '+str(x['preferredLabel']['string'])+'@'+str(x['preferredLabel']['language']))
        else:
            pass
        return choices

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
