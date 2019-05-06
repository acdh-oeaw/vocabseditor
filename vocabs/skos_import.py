import rdflib
from rdflib import Graph, Literal, Namespace, RDF, URIRef, RDFS, XSD
from rdflib.namespace import DC, RDFS, SKOS
from rdflib.util import guess_format
import pprint
from .models import *
import re
from .forms import UploadFileForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
import logging

logging.getLogger().setLevel(logging.INFO)


SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
DC = Namespace("http://purl.org/dc/elements/1.1/")
DCT = Namespace("http://purl.org/dc/terms/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
VOCABS = Namespace("https://vocabs.acdh.oeaw.ac.at/create-concept-scheme/")


class SkosImporter(object):
	"""
	Perform a file parsing and importing SKOS data in database
	"""

	def __init__(self, file, file_format=None, language=None):
		self.file = file
		self.file_format = file_format
		self.language = language

	def _graph_read(self):
		"""
		Parse a file in RDF Graph
		"""
		g = Graph()
		g.bind('skos', SKOS)
		g.bind('dc', DC)
		g.bind('dct', DCT)
		g.bind('rdfs', RDFS)
		g.parse(self.file)
		return g

	def parse_triples(self):
		"""
		Reads graph, finds triples about concept scheme and its concepts,
		returns a dictionary
		"""
		concept_scheme = {}
		g = self._graph_read()
		if (None, RDF.type, SKOS.ConceptScheme) in g:
			for x in g.subjects(RDF.type, SKOS.ConceptScheme):
				concept_scheme["identifier"] = str(x)
				for title in g.preferredLabel(x):
					concept_scheme["title"] = str(title[1])
					logging.info("Concept scheme data collected")
		else:
			raise ValueError("Graph doesn't have a Concept Scheme")
		logging.info("Concept Scheme: {}".format(concept_scheme))
		if (None, RDF.type, SKOS.Concept) in g:
			concepts = []
			for x in g.subjects(RDF.type, SKOS.Concept):
				concept = {}
				concept["legacy_id"] = str(x)
				# pref labels
				pref_labels = []
				for pref_label in g.preferredLabel(x):
					label = {}
					label["label"] = str(pref_label[1])
					lang = re.search("lang='(.{2,3})'", str(pref_label))
					if lang is not None:
						label["lang"] = lang.group(1)
					else:
						label["lang"] = "en"
					pref_labels.append(label)
				concept["pref_label"] = pref_labels

				for scheme in g.objects(x, SKOS.inScheme):
					concept["scheme"] = str(scheme)
				for notation in g.objects(x, SKOS.notation):
					concept["notation"] = str(notation)
				for creator in g.objects(x, DC.creator):
					concept["creator"] = str(creator)
				for contributor in g.objects(x, DC.contributor):
					concept["contributor"] = str(contributor)
				for broader_concept in g.objects(x, SKOS.broader):
					concept["broader_concept"] = str(broader_concept)
				concepts.append(concept)
			logging.info("Concepts: {}".format(concepts))
			concept_scheme["has_concepts"] = concepts
		else:
			ValueError("Graph doesn't have any concepts")
		return concept_scheme


	def upload_data(self):
		"""
		Creates and saves concepts scheme and its concepts in a database
		"""
		concept_scheme = self.parse_triples()
		concept_scheme_uri = concept_scheme.get("identifier")
		concept_scheme_title = concept_scheme.get("title")
		concept_scheme_has_concepts = concept_scheme.get("has_concepts")
		concept_scheme = SkosConceptScheme.objects.create(
			identifier=concept_scheme_uri,
			title=concept_scheme_title, created_by=User.objects.get(username='kzaytseva')
			)
		concept_scheme.save()
		for concept in concept_scheme_has_concepts:
			concept_legacy_id = concept.get("legacy_id")
			concept_inscheme = concept.get("scheme")
			concept_notation = concept.get("notation", "")
			concept_creator = concept.get("creator", "")
			concept_contributor = concept.get("contributor", "")
			for pref_label in concept.get("pref_label"):
				concept_pref_label = pref_label.get("label")
				concept_pref_label_lang = pref_label.get("lang")
			new_concept = SkosConcept.objects.create(
				legacy_id=concept_legacy_id,
				scheme=SkosConceptScheme.objects.get(identifier=concept_inscheme),
				pref_label=concept_pref_label, pref_label_lang=concept_pref_label_lang,
				notation=concept_notation, creator=concept_creator,
				contributor=concept_contributor, created_by=User.objects.get(username='kzaytseva')
				)
			new_concept.save()
		# add relationships
		for concept in concept_scheme_has_concepts:
			if concept.get("broader_concept") is not None:
				update_concept = SkosConcept.objects.filter(
					legacy_id=concept.get("legacy_id")).update(
					broader_concept=SkosConcept.objects.get(legacy_id=concept.get("broader_concept"))
					)
			else:
				pass
		return SkosConcept.objects.rebuild()

