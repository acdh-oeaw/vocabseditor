import rdflib
from django.conf import settings
from rdflib import Literal, Namespace, URIRef

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
DC = Namespace("http://purl.org/dc/elements/1.1/")
DCT = Namespace("http://purl.org/dc/terms/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
VOCABS = Namespace("https://vocabs.acdh.oeaw.ac.at/create-concept-scheme/")
VOCABS_SEPARATOR = getattr(settings, "VOCABS_SEPARATOR", "/")


RDF_FORMATS = {
    "xml": "rdf",
    "n3": "n3",
    "turtle": "ttl",
    "nt": "nt",
    "pretty-xml": "rdf",
    "trix": "trix",
    "trig": "trig",
    "nquads": "nq",
    "json-ld": ".jsonld",
}


def graph_construct_qs(results):
    g = rdflib.Graph()
    main_concept_scheme = results.first().scheme.get_subject()
    main_concept_scheme_graph = results.first().scheme.as_graph()
    g = g + main_concept_scheme_graph
    for obj in results:
        concept = URIRef(obj.create_uri())
        g.add((concept, SKOS.inScheme, main_concept_scheme))
        g = g + obj.as_graph()
        if obj.collection.all():
            for x in obj.collection.all():
                collection = x.get_subject()
                collection_graph = x.as_graph()
                g = g + collection_graph
                if x.creator:
                    for i in x.creator.split(";"):
                        g.add((collection, DC.creator, Literal(i.strip())))
                if x.contributor:
                    for i in x.contributor.split(";"):
                        g.add((collection, DC.contributor, Literal(i.strip())))
                if x.has_members.all():
                    for y in x.has_members.all():
                        if y.legacy_id:
                            g.add((collection, SKOS.member, URIRef(y.legacy_id)))
                        else:
                            g.add((collection, SKOS.member, URIRef(y.create_uri())))
    return g
