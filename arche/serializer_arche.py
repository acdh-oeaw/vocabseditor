import rdflib
from django.conf import settings
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef, RDFS, ConjunctiveGraph
from rdflib.namespace import DC, FOAF, RDFS, XSD
from rdflib.namespace import SKOS
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from entities.serializer_arche import place_to_arche, inst_to_arche, person_to_arche
from .helpers import arche_ids

ARCHE = Namespace('https://vocabs.acdh.oeaw.ac.at/schema#')
ACDH = Namespace('https://id.acdh.oeaw.ac.at/')
GEONAMES = Namespace('http://www.geonames.org/ontology#')
try:
    base_url = settings.ARCHE_SETTINGS['base_url']
except AttributeError:
    base_url = "https://please/provide/ARCHE-SETTINGS"

LOCATION_PATH = "Y:\OREA_DOKU_PLATTFORM-Thunau_Vers2_aktuell 08 03 2017"


def collection_to_arche(itmes):

    """takes queryset of Collections objects and returns an ARCHE rdflib.Graph"""

    g = rdflib.Graph()
    for obj in itmes:
        subject = arche_ids(obj, 'collection')
        print(subject)
        g.add((subject, RDF.type, ARCHE.Collection))
        if obj.has_title:
            g.add((subject, ARCHE.hasTitle, Literal(obj.has_title)))
        if obj.has_license:
            g.add((subject, ARCHE.hasLicense, Literal(obj.has_license)))
        if obj.description:
            g.add((subject, ARCHE.hasDescription, Literal(obj.description)))
        if obj.has_category:
            g.add((subject, ARCHE.hasCategory, URIRef(obj.has_category)))
        if obj.has_lcs:
            g.add((subject, ARCHE.hasLifeCycleStatus, URIRef(obj.has_lcs)))
        if obj.has_access_restriction:
            g.add((subject, ARCHE.hasAccessRestriction, URIRef(obj.has_access_restriction)))
        if obj.has_contributor.all():
            authors_g = person_to_arche(obj.has_contributor.all())
            g = g + authors_g
            for x in obj.has_contributor.all():
                temp_a = arche_ids(x, 'person',  id_prop='authority_url')
                g.add((subject, ARCHE.hasContributor, temp_a))
        if obj.part_of:
            temp_col = arche_ids(obj.part_of, 'collection')
            g.add((subject, ARCHE.isPartOf, temp_col))
    return g


def resource_to_arche(items):

    """takes queryset of Resources objects and returns an ARCHE rdflib.Graph"""

    g = rdflib.Graph()
    for obj in items:
        subject = arche_ids(obj, 'resource')
        g.add((subject, RDF.type, ARCHE.Resource))
        if obj.has_title:
            g.add((subject, ARCHE.hasTitle, Literal(obj.has_title)))
        if obj.has_license:
            g.add((subject, ARCHE.hasLicense, Literal(obj.has_license)))
        if obj.has_filetype:
            g.add((subject, ARCHE.hasFormat, Literal(obj.has_filetype)))
        if obj.file_size:
            g.add((subject, ARCHE.hasBinarySize, Literal(obj.file_size)))
        if obj.description:
            g.add((subject, ARCHE.hasDescription, Literal(obj.description)))
        if obj.has_category:
            g.add((subject, ARCHE.hasCategory, URIRef(obj.has_category)))
        if obj.has_lcs:
            g.add((subject, ARCHE.hasLifeCycleStatus, URIRef(obj.has_lcs)))
        if obj.has_access_restriction:
            g.add((subject, ARCHE.hasAccessRestriction, URIRef(obj.has_access_restriction)))
        if obj.has_contributor.all():
            authors_g = person_to_arche(obj.has_contributor.all())
            g = g + authors_g
            for x in obj.has_contributor.all():
                temp_a = arche_ids(x, 'person',  id_prop='authority_url')
                g.add((subject, ARCHE.hasContributor, temp_a))
            authors_g = None
            temp_a = None
        if obj.has_contributor.all():
            authors_g = person_to_arche(obj.has_contributor.all())
            g = g + authors_g
            for x in obj.has_contributor.all():
                temp_a = arche_ids(x, 'person',  id_prop='authority_url')
                g.add((subject, ARCHE.hasContributor, temp_a))
            authors_g = None
            temp_a = None
        if obj.has_creator.all():
            authors_g = person_to_arche(obj.has_creator.all())
            g = g + authors_g
            for x in obj.has_creator.all():
                temp_a = arche_ids(x, 'person',  id_prop='authority_url')
                g.add((subject, ARCHE.hasCreator, temp_a))
            authors_g = None
            temp_a = None
        if obj.part_of:
            coll_g = collection_to_arche([obj.part_of])
            g = g + coll_g
            temp_col = arche_ids(obj.part_of, 'collection')
            g.add((subject, ARCHE.isPartOf, temp_col))
    return g


def project_to_arche(itmes):

    """takes queryset of Projects objects and returns an ARCHE rdflib.Graph"""

    g = rdflib.Graph()
    for obj in itmes:
        subject = arche_ids(obj, 'project')
        g.add((subject, RDF.type, ARCHE.Project))
        if obj.has_title:
            g.add((subject, ARCHE.hasTitle, Literal(obj.has_title)))
        if obj.description:
            g.add((subject, ARCHE.hasDescription, Literal(obj.description)))
        if obj.has_start_date:
            g.add((subject, ARCHE.hasStartDate, Literal(obj.has_start_date, datatype=XSD.date)))
        if obj.has_end_date:
            g.add((subject, ARCHE.hasEndDate, Literal(obj.has_end_date, datatype=XSD.date)))
        if obj.has_category:
            g.add((subject, ARCHE.hasCategory, URIRef(obj.has_category)))
        if obj.has_lcs:
            g.add((subject, ARCHE.hasLifeCycleStatus, URIRef(obj.has_lcs)))
        if obj.has_contributor.all():
            authors_g = person_to_arche(obj.has_contributor.all())
            g = g + authors_g
            for x in obj.has_contributor.all():
                temp_a = arche_ids(x, 'person',  id_prop='authority_url')
                g.add((subject, ARCHE.hasContributor, temp_a))
        if obj.related_collection.all():
            col_g = collection_to_arche(obj.related_collection.all())
            g = g + col_g
            for x in obj.related_collection.all():
                temp_col = arche_ids(x, 'collection')
                g.add((subject, ARCHE.hasRelatedCollection, temp_col))
        if obj.has_funder.all():
            inst_g = inst_to_arche(obj.has_funder.all())
            g = g + inst_g
            for x in obj.has_funder.all():
                temp_inst = arche_ids(x, 'institution', id_prop="authority_url")
                g.add((subject, ARCHE.hasFunder, temp_inst))
    return g
