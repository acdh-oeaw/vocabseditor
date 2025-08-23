import rdflib
from django.conf import settings
from rdflib import RDF, XSD, Literal, Namespace, URIRef

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
    g.bind("skos", SKOS)
    g.bind("dc", DC)
    g.bind("dct", DCT)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    main_concept_scheme = results.first().scheme.get_subject()
    main_concept_scheme_graph = results.first().scheme.as_graph()
    g = g + main_concept_scheme_graph
    for obj in results:
        # Concept properties
        # TODO user entered URI
        # if obj.legacy_id:
        #     concept = URIRef(obj.legacy_id)
        # else:
        #     concept = URIRef(main_concept_scheme + VOCABS_SEPARATOR + "concept" + str(obj.id))
        concept = URIRef(obj.create_uri())
        g.add((concept, RDF.type, SKOS.Concept))
        g.add((concept, SKOS.prefLabel, Literal(obj.pref_label, lang=obj.pref_label_lang)))
        if obj.notation != "":
            g.add((concept, SKOS.notation, Literal(obj.notation)))
        # each concept must have skos:inScheme main_concept_scheme
        g.add((concept, SKOS.inScheme, main_concept_scheme))
        if obj.collection.all():
            for x in obj.collection.all():
                collection = x.get_subject()
                collection_graph = x.as_graph()
                g = g + collection_graph
                # Collection sources
                if x.has_sources.all():
                    for source in x.has_sources.all():
                        g.add(
                            (
                                collection,
                                DC.source,
                                Literal(source.name, lang=source.language),
                            )
                        )
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
        # Concept properties
        if obj.has_labels.all():
            for label in obj.has_labels.all():
                if label.label_type == "prefLabel":
                    g.add(
                        (
                            concept,
                            SKOS.prefLabel,
                            Literal(label.name, lang=label.language),
                        )
                    )
                elif label.label_type == "altLabel":
                    g.add(
                        (
                            concept,
                            SKOS.altLabel,
                            Literal(label.name, lang=label.language),
                        )
                    )
                elif label.label_type == "hiddenLabel":
                    g.add(
                        (
                            concept,
                            SKOS.hiddenLabel,
                            Literal(label.name, lang=label.language),
                        )
                    )
                # if label.label_type is not set then make it altLabel
                else:
                    g.add(
                        (
                            concept,
                            SKOS.altLabel,
                            Literal(label.name, lang=label.language),
                        )
                    )
        if obj.has_notes.all():
            for note in obj.has_notes.all():
                if note.note_type == "note":
                    g.add((concept, SKOS.note, Literal(note.name, lang=note.language)))
                elif note.note_type == "scopeNote":
                    g.add(
                        (
                            concept,
                            SKOS.scopeNote,
                            Literal(note.name, lang=note.language),
                        )
                    )
                elif note.note_type == "changeNote":
                    g.add(
                        (
                            concept,
                            SKOS.changeNote,
                            Literal(note.name, lang=note.language),
                        )
                    )
                elif note.note_type == "editorialNote":
                    g.add(
                        (
                            concept,
                            SKOS.editorialNote,
                            Literal(note.name, lang=note.language),
                        )
                    )
                elif note.note_type == "historyNote":
                    g.add(
                        (
                            concept,
                            SKOS.historyNote,
                            Literal(note.name, lang=note.language),
                        )
                    )
                elif note.note_type == "definition":
                    g.add(
                        (
                            concept,
                            SKOS.definition,
                            Literal(note.name, lang=note.language),
                        )
                    )
                elif note.note_type == "example":
                    g.add((concept, SKOS.example, Literal(note.name, lang=note.language)))
                else:
                    g.add((concept, SKOS.note, Literal(note.name, lang=note.language)))
        if obj.has_sources.all():
            for source in obj.has_sources.all():
                g.add((concept, DC.source, Literal(source.name, lang=source.language)))
        # top concepts
        if not obj.broader_concept:
            g.add((main_concept_scheme, SKOS.hasTopConcept, URIRef(concept)))
            g.add((concept, SKOS.topConceptOf, main_concept_scheme))
        # modelling broader/narrower relationships
        if obj.broader_concept:
            g.add((concept, SKOS.broader, URIRef(obj.broader_concept.create_uri())))
        if obj.narrower_concepts.all():
            for x in obj.narrower_concepts.all():
                g.add((concept, SKOS.narrower, URIRef(x.create_uri())))
        # modelling external matches
        # skos:related
        if obj.related:
            for x in obj.related_as_list():
                g.add((concept, SKOS.related, URIRef(x)))
        # skos:broadMatch
        if obj.broad_match:
            for x in obj.broad_match_as_list():
                g.add((concept, SKOS.broadMatch, URIRef(x)))
        # skos:narrowMatch
        if obj.narrow_match:
            for x in obj.narrow_match_as_list():
                g.add((concept, SKOS.narrowMatch, URIRef(x)))
        # skos:exactMatch
        if obj.exact_match:
            for x in obj.exact_match_as_list():
                g.add((concept, SKOS.exactMatch, URIRef(x)))
        # skos:relatedMatch
        if obj.related_match:
            for x in obj.related_match_as_list():
                g.add((concept, SKOS.relatedMatch, URIRef(x)))
        # skos:closeMatch
        if obj.close_match:
            for x in obj.close_match_as_list():
                g.add((concept, SKOS.closeMatch, URIRef(x)))
        # meta
        if obj.creator:
            for i in obj.creator.split(";"):
                g.add((concept, DC.creator, Literal(i.strip())))
        if obj.contributor:
            for i in obj.contributor.split(";"):
                g.add((concept, DC.contributor, Literal(i.strip())))
        if obj.date_created:
            g.add((concept, DCT.created, Literal(obj.date_created, datatype=XSD.dateTime)))
        if obj.date_modified:
            g.add(
                (
                    concept,
                    DCT.modified,
                    Literal(obj.date_modified, datatype=XSD.dateTime),
                )
            )
    return g
