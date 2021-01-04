import os

from django.test import TestCase
from django.contrib.auth.models import User
from rdflib import Graph

from .constants import USER
from ..models import SkosConceptScheme, SkosCollection, SkosConcept
from ..skos_import import SkosImporter
from ..rdf_utils import graph_construct_qs


EXAMPLE_SKOS_IMPORT = os.path.join(os.path.dirname(__file__), "example_skos_import.rdf")
EXAMPLE_SKOS_EXPORT = os.path.join(os.path.dirname(__file__), "example_skos_export.rdf")


class TestSkosImport(TestCase):
    """ Test module for SKOS import functionality. """

    def setUp(self) -> None:
        self.user = User.objects.create_user(**USER)
        skos_vocab = SkosImporter(file=EXAMPLE_SKOS_IMPORT, file_format="xml", language="en")
        self.concept_scheme = skos_vocab.parse_triples()
        skos_vocab.upload_data(self.user)

    def test_parsing_to_graph(self):
        self.assertEqual(type(self.concept_scheme), dict)
        self.assertEqual(self.concept_scheme["identifier"], "https://vocabs.acdh.oeaw.ac.at/dhataxonomy/ConceptScheme")
        self.assertEqual(type(self.concept_scheme["title"]), list)
        self.assertEqual(self.concept_scheme["title"][0]["title"], "DHA Taxonomy")
        self.assertEqual(self.concept_scheme["title"][0]["lang"], "en")

    def test_uploading_data(self):
        self.assertEqual(len(SkosConceptScheme.objects.all()), 1)
        self.assertEqual(len(SkosCollection.objects.all()), 6)
        self.assertEqual(len(SkosConcept.objects.all()), 114)


class TestSkosExport(TestCase):
    """ Test module for SKOS export functionality. """

    def setUp(self) -> None:
        self.user = User.objects.create_user(**USER)
        skos_vocab = SkosImporter(file=EXAMPLE_SKOS_EXPORT, file_format="xml", language="en")
        self.concept_scheme = skos_vocab.parse_triples()
        skos_vocab.upload_data(self.user)

    def test_skos_export(self):
        g = graph_construct_qs(SkosConcept.objects.all())
        self.assertEqual(Graph, type(g))
