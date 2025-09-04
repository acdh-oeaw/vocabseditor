import os

from django.conf import settings
from github import Github, InputGitTreeElement
from rdflib import Graph, Literal, URIRef, namespace


class MyGraph(Graph):
    def preferredLabel(
        self,
        subject,
        lang=None,
        default=None,
        labelProperties=(namespace.SKOS.prefLabel, namespace.RDFS.label),
    ):
        """
        Find the preferred label for subject.
        By default prefers skos:prefLabels over rdfs:labels. In case at least
        one prefLabel is found returns those, else returns labels. In case a
        language string (e.g., "en", "de" or even "" for no lang-tagged
        literals) is given, only such labels will be considered.
        Return a list of (labelProp, label) pairs, where labelProp is either
        skos:prefLabel or rdfs:label.
        >>> from rdflib import ConjunctiveGraph, URIRef, Literal, namespace
        >>> from pprint import pprint
        >>> g = ConjunctiveGraph()
        >>> u = URIRef("http://example.com/foo")
        >>> g.add([u, namespace.RDFS.label, Literal("foo")]) # doctest: +ELLIPSIS
        <Graph identifier=... (<class 'rdflib.graph.ConjunctiveGraph'>)>
        >>> g.add([u, namespace.RDFS.label, Literal("bar")]) # doctest: +ELLIPSIS
        <Graph identifier=... (<class 'rdflib.graph.ConjunctiveGraph'>)>
        >>> pprint(sorted(g.preferredLabel(u)))
        [(rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'),
          rdflib.term.Literal('bar')),
         (rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'),
          rdflib.term.Literal('foo'))]
        >>> g.add([u, namespace.SKOS.prefLabel, Literal("bla")]) # doctest: +ELLIPSIS
        <Graph identifier=... (<class 'rdflib.graph.ConjunctiveGraph'>)>
        >>> pprint(g.preferredLabel(u))
        [(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
          rdflib.term.Literal('bla'))]
        >>> g.add([u, namespace.SKOS.prefLabel, Literal("blubb", lang="en")]) # doctest: +ELLIPSIS
        <Graph identifier=... (<class 'rdflib.graph.ConjunctiveGraph'>)>
        >>> sorted(g.preferredLabel(u)) #doctest: +NORMALIZE_WHITESPACE
        [(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
          rdflib.term.Literal('bla')),
          (rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
          rdflib.term.Literal('blubb', lang='en'))]
        >>> g.preferredLabel(u, lang="") #doctest: +NORMALIZE_WHITESPACE
        [(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
          rdflib.term.Literal('bla'))]
        >>> pprint(g.preferredLabel(u, lang="en"))
        [(rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel'),
          rdflib.term.Literal('blubb', lang='en'))]
        """
        if default is None:
            default = []

        # setup the language filtering
        if lang is not None:
            if lang == "":  # we only want not language-tagged literals

                def langfilter(l_):
                    return l_.language is None

            else:

                def langfilter(l_):
                    return l_.language == lang

        else:  # we don't care about language tags

            def langfilter(l_):
                return True

        for labelProp in labelProperties:
            labels = list(filter(langfilter, self.objects(subject, labelProp)))
            if len(labels) == 0:
                continue
            else:
                return [(labelProp, l_) for l_ in labels]
        return default


def modelprops_to_graph(obj, subj, g):
    for field in obj._meta.fields:
        if hasattr(field, "extra") and "predicate" in field.extra:
            value = getattr(obj, field.name)
            if value:
                predicate = field.extra["predicate"]
                if "splitter" in field.extra:
                    splitter = field.extra["splitter"]
                    for item in value.split(splitter):
                        item = item.strip()
                        if item:
                            if field.extra.get("as_uri"):
                                g.add((subj, predicate, URIRef(item)))
                            else:
                                try:
                                    g.add((subj, predicate, Literal(item, datatype=field.extra["datatype"])))
                                except KeyError:
                                    g.add((subj, predicate, Literal(item)))
                else:
                    try:
                        g.add((subj, predicate, Literal(value, datatype=field.extra["datatype"])))
                    except KeyError:
                        g.add((subj, predicate, Literal(value)))
    return g


def push_to_gh(
    files,
    ghpat=settings.GHPAT,
    repo_name=settings.GHREPO,
    branch="master",
    commit_message="some message",
):
    g = Github(ghpat)
    repo = g.get_repo(repo_name)
    master_ref = repo.get_git_ref(f"heads/{branch}")
    master_sha = master_ref.object.sha
    base_tree = repo.get_git_tree(master_sha)
    element_list = list()
    for entry in files:
        _, file_name = os.path.split(entry)
        with open(entry) as input_file:
            data = input_file.read()
        element = InputGitTreeElement(f"dumps/{file_name}", "100644", "blob", data)
        element_list.append(element)
    tree = repo.create_git_tree(element_list, base_tree)
    parent = repo.get_git_commit(master_sha)
    commit = repo.create_git_commit(commit_message, tree, [parent])
    master_ref.edit(commit.sha)


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


def handle_uploaded_file(file):
    file_name = file.name
    full_file_name = os.path.join(settings.MEDIA_ROOT, "uploads", file_name)
    with open(full_file_name, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return full_file_name


def delete_legacy_ids(concept_scheme):
    concept_scheme.legacy_id = ""
    for x in concept_scheme.has_concepts.all():
        x.legacy_id = ""
        x.save()
    concept_scheme.save()
    return "done"


def delete_skos_notations(concept_scheme):
    for x in concept_scheme.has_concepts.all():
        x.notation = ""
        x.save()
    return "done"
