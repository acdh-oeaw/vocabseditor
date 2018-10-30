import re
import requests
import json
import rdflib
from rdflib.namespace import RDF, FOAF
from rdflib import Namespace


def fetch_coords(place):
    """takes a place object, checks if a gnd id is assigned and if so fetches lat and long"""
    gn = place.geonames_id
    base = "http://sws.geonames.org/{}/about.rdf"
    if gn:
        url = base.format(gn)
        g = rdflib.Graph()
        result = g.parse(url)
        wgs84_pos = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
        for s, p, o in result.triples((None, wgs84_pos.lat, None)):
            lat = float(o)
        for s, p, o in result.triples((None, wgs84_pos.long, None)):
            lng = float(o)
        place.lat = lat
        place.lng = lng
        place.save()
        return place
    else:
        return place


# example usage
# for x in Place.objects.filter(lat__isnull=True):
#     fetch_coords(x)
