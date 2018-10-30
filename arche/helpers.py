from .models import Collection
from django.conf import settings
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from rdflib import URIRef, Graph
from rdflib.namespace import SKOS, RDF

try:
    base_url = settings.ARCHE_SETTINGS['base_url']
except AttributeError:
    base_url = "https://please/provide/ARCHE-SETTINGS"


def arche_ids(obj, class_name, base_url=base_url, id_prop='acdh_id'):
    """checks if an object has a valid(!) arche_id and returns this,\
    if not it returns a generic id"""

    custom_id = getattr(obj, id_prop, None)
    print(custom_id)
    if custom_id:
        try:
            g = Graph()
            subject = URIRef(str(custom_id))
            g.add((subject, RDF.type, SKOS.Concept))
            g.serialize(format='nt')
            subject = URIRef(str(custom_id))
        except:
            subject = URIRef('/'.join([base_url, class_name, str(str(obj.id))]))
    else:
        subject = URIRef('/'.join([base_url, class_name, str(obj.id)]))
    return subject


def path2cols(path, separator="_"):
    """takes a splittable string and creates nested collections"""
    counter = 1
    current = 0
    cols = []
    path_parts = path.split(separator)[:-1]
    path_length = len(path_parts)
    prefix = path_length
    for x in reversed(path_parts):
        col_title = '/'.join(path_parts[0:prefix])
        col, _ = Collection.objects.get_or_create(
            has_title=col_title
        )
        cols.append(col)
        prefix = prefix - 1
    while counter != len(cols):
        current_col = cols[current]
        parent_col = cols[counter]
        current_col.part_of = parent_col
        current_col.save()
        counter += 1
        current += 1
    return cols


def create_acdhid(resource, trim=0, base_url='https://id.acdh.oeaw.ac.at', preserve=False):
    """
    Function to process text from the ACDH internal json standard

    param *resource*: a Collection or Resource object:
    param *trim*: a interger value providing an index for cutting the beginning of string
    param *base_url*: a base url of the identifier with default 'https://id.acdh.oeaw.ac.at'
    param *preserve*: if true nothing happens.
    """
    if preserve:
        return resource
    else:
        if base_url.endswith('/'):
            base_url = base_url[:-1]
            print(base_url)
        try:
            id_ending = "{}".format(resource.label()[trim:])
            acdhid = "/".join([base_url, id_ending])
            resource.acdh_id = acdhid
        except TypeError:
            id_ending = "{}".format(resource.label())
            acdhid = "/".join([base_url, id_ending])
            resource.acdh_id = acdhid
        resource.save()
        return resource
