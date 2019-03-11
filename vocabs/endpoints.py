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

    def payload(self, q):
        """
        returns a dictionary containing arguments to be
        passed in the URL’s query string
        """
        return {'QueryString': q}

    def get_url(self):
        """
        service's URL
        """
        return self.endpoint+self.search_type

    def parse_response(self, response):
        """
        parses JSON response to return a list containing
        data in format 'uri - label'
        """
        results = []
        for x in response['results']:
            results.append(str(x['uri'])+' - '+str(x['label']))
        return results


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
        results = []
        for x in response:
            results.append(str(x['id'])+' - '+str(x['label']))
        return results


class GemetAC(object):
    """
    GEMET Thesaurus
    """
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
    """
    FISH Vocabularies
    """
    endpoint = 'https://www.heritagedata.org/live/services/'
    search_type = 'getConceptLabelMatch?'
    scheme_dict = {
        "fish event": "http://purl.org/heritagedata/schemes/agl_et",
        "fish thesaurus": "http://purl.org/heritagedata/schemes/560",
        "fish monument types": "http://purl.org/heritagedata/schemes/eh_tmt2",
        "fish objects": "http://purl.org/heritagedata/schemes/mda_obj"
    }

    def payload(self, scheme, q):
        payload = {'schemeURI': scheme, 'contains': q}
        return payload

    def get_url(self):
        return self.endpoint+self.search_type

    def parse_response(self, response):
        results = []
        for x in response:
            results.append(str(x['uri'])+' - '+str(x['label']))
        return results


ENDPOINT = {
    'dbpedia': DbpediaAC(),
    'gnd': GndAC(),
    'gemet': GemetAC(),
    'fish event': FishAC(),
    'fish thesaurus': FishAC(),
    'fish monument types': FishAC(),
    'fish objects': FishAC()
}

ENDPOINT_CHOICES = [(key, key) for key, value in ENDPOINT.items()]
