############################ ENDPOINTS TO QUERY EXTERNAL CONCEPTS FOR MATCH ############################
ENDPOINTS = [
    ('http://lookup.dbpedia.org/api/search/', 'Dbpedia'),
    ('https://lobid.org/gnd/search?', 'GND'),
    ('https://www.eionet.europa.eu/gemet/', 'GEMET'),
    ('https://www.heritagedata.org/live/services/',
                'FISH Archaeological Sciences Thesaurus'),
    # ('FISH – The Forum on Information Standards in Heritage', (
    #         ('https://www.heritagedata.org/live/services/getConceptLabelMatch?schemeURI=http://purl.org/heritagedata/schemes/560&contains=',
    #             'FISH Archaeological Sciences Thesaurus'),
    #         ('https://www.heritagedata.org/live/services/getConceptLabelMatch?schemeURI=http://purl.org/heritagedata/schemes/agl_et&contains=',
    #             'FISH Event Types Thesaurus'),
    #         ('https://www.heritagedata.org/live/services/getConceptLabelMatch?schemeURI=http://purl.org/heritagedata/schemes/eh_tbm&contains=',
    #             'FISH Building Materials Thesaurus'),
    #         ('https://www.heritagedata.org/live/services/getConceptLabelMatch?schemeURI=http://purl.org/heritagedata/schemes/eh_tmt2&contains=',
    #             'FISH Thesaurus of Monument Types'),
    #         ('https://www.heritagedata.org/live/services/getConceptLabelMatch?schemeURI=http://purl.org/heritagedata/schemes/mda_obj&contains=',
    #             'FISH Archaeological Objects Thesaurus'),
    #     )
    # ),
]


search_types = (
    ('KeywordSearch?', 'Keyword Search'),
    ('PrefixSearch?', 'Prefix Search')
    )


class GeneralAC(object):
    pass

    def get_url(self):
        url = self.endpoint+self.search_type+self.query+'='
        return str(url)


class DbpediaAC(GeneralAC):
    endpoint = 'http://lookup.dbpedia.org/api/search/'
    search_type = 'PrefixSearch?'
    query = 'QueryString'

    def get_url(self):
        url = self.endpoint+self.search_type+self.query+'='
        return str(url)

    def parse_response(self, response):
        results = []
        for x in response['results']:
            results.append(str(x['uri'])+' - '+str(x['label']))
        return results


class GndAC(GeneralAC):
    endpoint = 'https://lobid.org/gnd/search?'
    search_type = 'format=json:preferredName&'
    query = 'q'


    def parse_response(self, response):
        results = []
        for x in response:
            results.append(str(x['id'])+' - '+str(x['label']))
        return results


class GemetAC(GeneralAC):
    endpoint = 'https://www.eionet.europa.eu/gemet/'
    search_type = 'getConceptsMatchingKeyword?&'
    parameter = 'search_mode=4&'
    query = 'keyword'

    def get_url(self):
        url = self.endpoint+self.search_type+self.parameter+self.query+'='
        return str(url)

    def parse_response(self, response):
        results = []
        for x in response:
            results.append(str(x['uri'])+' - '+str(x['preferredLabel']['string'])+'@'+str(x['preferredLabel']['language']))
        return results


class FishAC(GeneralAC):
    endpoint = 'https://www.heritagedata.org/live/services/'
    search_type = 'getConceptLabelMatch?'
    parameter = 'schemeURI=http://purl.org/heritagedata/schemes/560&'
    query = 'contains'

    def get_url(self):
        url = self.endpoint+self.search_type+self.parameter+self.query+'='
        return str(url)

    def parse_response(self, response):
        results = []
        for x in response:
            results.append(str(x['uri'])+' - '+str(x['label']))
        return results
