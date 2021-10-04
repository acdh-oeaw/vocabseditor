"""
Settings for external services to query for autocomplete
when assigning skos Matches
"""

search_types = (
    ('KeywordSearch?', 'Keyword Search'),
    ('PrefixSearch?', 'Prefix Search')
)


class DbpediaAC(object):
    """
    Dbpedia
    """
    endpoint = 'http://lookup.dbpedia.org/api/search/'
    search_type = 'PrefixSearch?'
    response_format = 'json'

    def payload(self, q):
        """
        returns a dictionary containing arguments to be
        passed in the URL’s query string
        """
        return {'QueryString': q, 'format': self.response_format}

    def get_url(self):
        """
        service's URL
        """
        return self.endpoint + self.search_type

    def parse_response(self, response):
        """
        parses JSON response to return a list containing
        data in format 'uri - label'
        """
        return [str(x['resource'][0]) for x in response['docs']]


class GndAC(object):
    """
    GND
    """
    endpoint = 'https://lobid.org/gnd/search?'

    def payload(self, q):
        return {'format': 'json:preferredName', 'q': q}

    def get_url(self):
        return self.endpoint

    def parse_response(self, response):
        return [str(x['id']) + ' - ' + str(x['label']) for x in response]


class GemetAC(object):
    """
    GEMET Thesaurus
    """
    endpoint = 'https://www.eionet.europa.eu/gemet/'
    search_type = 'getConceptsMatchingKeyword?'

    def payload(self, q):
        return {'search_mode': '4', 'keyword': q}

    def get_url(self):
        return self.endpoint + self.search_type

    def parse_response(self, response):
        return [str(x['uri']) + ' - ' + str(x['preferredLabel']['string']) for x in response]


class FishAC(object):
    """
    FISH Vocabularies
    """
    endpoint = 'https://www.heritagedata.org/live/services/'
    search_type = 'getConceptLabelMatch?'
    scheme_dict = {
        "FISH Event Types Thesaurus": "http://purl.org/heritagedata/schemes/agl_et",
        "FISH Archaeological Sciences Thesaurus": "http://purl.org/heritagedata/schemes/560",
        "FISH Thesaurus of Monument Types": "http://purl.org/heritagedata/schemes/eh_tmt2",
        "FISH Archaeological Objects Thesaurus": "http://purl.org/heritagedata/schemes/mda_obj"
    }

    def payload(self, scheme, q):
        payload = {'schemeURI': scheme, 'contains': q}
        return payload

    def get_url(self):
        return self.endpoint + self.search_type

    def parse_response(self, response):
        return [str(x['uri']) + ' - ' + str(x['label']) for x in response]


ENDPOINT = {
    'Dbpedia': DbpediaAC(),
    'GND': GndAC(),
    'GEMET': GemetAC(),
    'FISH Event Types Thesaurus': FishAC(),
    'FISH Archaeological Sciences Thesaurus': FishAC(),
    'FISH Thesaurus of Monument Types': FishAC(),
    'FISH Archaeological Objects Thesaurus': FishAC()
}

ENDPOINT_CHOICES = [(key, key) for key, value in ENDPOINT.items()]
