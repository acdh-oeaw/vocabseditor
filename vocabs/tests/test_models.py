from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.contrib.auth.models import User

from .constants import *
from ..models import SkosConceptScheme, SkosCollection, SkosConcept


class ConceptSchemeTest(TestCase):
    """ Test module for SkosConceptScheme model """

    def setUp(self):
        self.user = User.objects.create_user(**USER)
        self.concept_scheme = SkosConceptScheme.objects.create(**concept_scheme(self.user))

    def test_create(self):
        concept_scheme = SkosConceptScheme.objects.get(title="Test Concept Scheme")
        self.assertEqual(concept_scheme.title, "Test Concept Scheme")
        self.assertEqual(len(SkosConceptScheme.objects.all()), 1)


class CollectionTest(TestCase):
    """ Test module for SkosCollection model """

    def setUp(self):
        self.user = User.objects.create_user(**USER)
        self.concept_scheme = SkosConceptScheme.objects.create(**concept_scheme(self.user))
        self.collection = SkosCollection.objects.create(**collection(self.concept_scheme, self.user))

    def test_create(self):
        collection = SkosCollection.objects.get(name="Test Collection")
        self.assertEqual(collection.name, "Test Collection")
        self.assertEqual(len(SkosCollection.objects.all()), 1)


class ConceptTest(TestCase):
    """ Test module for SkosConcept model """

    def setUp(self):
        self.user = User.objects.create_user(**USER)
        self.concept_scheme = SkosConceptScheme.objects.create(**concept_scheme(self.user))
        self.collection = SkosCollection.objects.create(**collection(self.concept_scheme, self.user))
        self.concept = SkosConcept.objects.create(**concept(self.concept_scheme, "Concept 1", self.user))

    def test_create(self):
        concept_one = SkosConcept.objects.get(pref_label="Concept 1")
        self.assertEqual(concept_one.pref_label, "Concept 1")
        self.assertEqual(len(SkosConcept.objects.all()), 1)
