############################ ENDPOINTS TO QUERY EXTERNAL CONCEPTS FOR MATCH ############################
ENDPOINTS = [
    ('http://lookup.dbpedia.org/api/search/', 'Dbpedia'),
    ('https://lobid.org/gnd/search?', 'GND'),
    ('https://www.eionet.europa.eu/gemet/', 'GEMET'),
    ('https://www.heritagedata.org/live/services/',
                'FISH Archaeological Sciences Thesaurus'),
    # ('https://www.heritagedata.org/live/services/getConceptLabelMatch?schemeURI=http://purl.org/heritagedata/schemes/mda_obj&contains=',
    #              'FISH Archaeological Objects Thesaurus'),
    # ('FISH – The Forum on Information Standards in Heritage', (
    #         ('http://purl.org/heritagedata/schemes/560',
    #             'FISH Archaeological Sciences Thesaurus'),
    #         ('http://purl.org/heritagedata/schemes/agl_et',
    #             'FISH Event Types Thesaurus'),
    #         ('http://purl.org/heritagedata/schemes/eh_tbm',
    #             'FISH Building Materials Thesaurus'),
    #         ('http://purl.org/heritagedata/schemes/eh_tmt2',
    #             'FISH Thesaurus of Monument Types'),
    #         ('http://purl.org/heritagedata/schemes/mda_obj',
    #             'FISH Archaeological Objects Thesaurus'),
    #     )
    # ),
]


search_types = (
    ('KeywordSearch?', 'Keyword Search'),
    ('PrefixSearch?', 'Prefix Search')
    )


class DbpediaAC(object):
    endpoint = 'http://lookup.dbpedia.org/api/search/'
    search_type = 'PrefixSearch?'

    def payload(self, q):
        return {'QueryString': q}

    def get_url(self):
        return self.endpoint+self.search_type

    def parse_response(self, response):
        results = []
        for x in response['results']:
            results.append(str(x['uri'])+' - '+str(x['label']))
        return results


class GndAC(object):
    endpoint = 'https://lobid.org/gnd/search?'
    #search_type = 'format=json:preferredName&'

    def payload(self, q):
        return {'format': 'json:preferredName', 'q': q}

    def get_url(self):
        return self.endpoint

    def parse_response(self, response):
        results = []
        for x in response:
            results.append(str(x['id'])+' - '+str(x['label']))
        return results


class GemetAC(object):
    endpoint = 'https://www.eionet.europa.eu/gemet/'
    search_type = 'getConceptsMatchingKeyword?'

    def payload(self, q):
        return {'search_mode': '4', 'keyword': q}

    def get_url(self):
        return self.endpoint+self.search_type

    def parse_response(self, response):
        results = []
        for x in response:
            results.append(str(x['uri'])+' - '+str(x['preferredLabel']['string'])+'@'+str(x['preferredLabel']['language']))
        return results


class FishAC(object):
    endpoint = 'https://www.heritagedata.org/live/services/'
    search_type = 'getConceptLabelMatch?'

    def payload(self, scheme, q):
        payload = {'schemeURI': scheme, 'contains': q}
        return payload

    def get_url(self):
        return self.endpoint+self.search_type

    # def get_url(self):
    #     url = self.endpoint+self.search_type+self.parameter+self.query+'='
    #     return str(url)

    def parse_response(self, response):
        results = []
        for x in response:
            results.append(str(x['uri'])+' - '+str(x['label']))
        return results
