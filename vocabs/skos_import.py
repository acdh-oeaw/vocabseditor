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
		g.parse(self.file, format=self.file_format)
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
				titles = []
				for title in g.preferredLabel(x, labelProperties=((DC.title), (RDFS.label), (DCT.title), (SKOS.prefLabel))):
					temp_title = {}
					temp_title["title"] = str(title[1])
					if str(title[1].language) == "None":
						temp_title["title_lang"] = "en"
						
					else:
						temp_title["title_lang"] = str(title[1].language)
						#print("TEMP LANG {}".format(type(title[1].language)))
					titles.append(temp_title)
					print("TEMP title {}".format(temp_title))
				concept_scheme["title"] = titles
				print("TITLES {}".format(titles))
				# for creator in g.objects(x, DC.creator):
				# 	concept_scheme["creator"] = str(creator)
				# for contributor in g.objects(x, DC.contributor):
				# 	concept_scheme["contributor"] = str(contributor)
				# for contributor in g.objects(x, DC.contributor):
				# 	concept_scheme["contributor"] = str(contributor)
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
					label["lang"] = str(pref_label[1].language)
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
				alt_labels = [] 
				for alt_label in g.objects(x, SKOS.altLabel):
					label = {}
					label["label"] = str(alt_label)
					if str(alt_label.language) == "None":
						label["lang"] = self.language
					else:
						label["lang"] = alt_label.language
					alt_labels.append(label)
				concept["alt_label"] = alt_labels
				hidden_labels = [] 
				for hidden_label in g.objects(x, SKOS.hiddenLabel):
					label = {}
					label["label"] = str(hidden_label)
					if str(hidden_label.language) == "None":
						label["lang"] = self.language
					else:
						label["lang"] = hidden_label.language
					hidden_labels.append(label)
				concept["hidden_label"] = hidden_labels
				notes = []
				predicates = [SKOS.note, SKOS.definition, SKOS.scopeNote, SKOS.changeNote,
							 SKOS.editorialNote, SKOS.historyNote, SKOS.example]
				for pred in predicates:
					for note in g.objects(x, pred):
						temp_note = {}
						temp_note["name"] = str(note)
						temp_note["lang"] = note.language
						temp_note["note_type"] = re.search('http.*#(.*)', str(pred)).group(1)
						notes.append(temp_note)
				concept["note"] = notes
				# Add concept to a list
				concepts.append(concept)
			#logging.info("Concepts: {}".format(concepts))
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
		concept_scheme_has_concepts = concept_scheme.get("has_concepts")
		main_title = {}
		other_titles = []
		for title in concept_scheme.get("title"):
			if title.get("title_lang") == self.language:
				main_title["label"] = title.get("title")
				main_title["lang"] = title.get("title_lang")
			else:
				other_title = {}
				other_title["label"] = title.get("title", "other title")
				other_title["lang"] = title.get("title_lang", "en") 
				other_titles.append(other_title)
		concept_scheme_title = main_title.get("label", "No title in specified language")
		concept_scheme_title_lang = main_title.get("lang", self.language)
		concept_scheme = SkosConceptScheme.objects.create(
			identifier=concept_scheme_uri,
			title=concept_scheme_title, title_lang=concept_scheme_title_lang,
			created_by=User.objects.get(username='kzaytseva')
			)
		concept_scheme.save()
		if  len(other_titles) > 0:
			for other in other_titles:
				cs_title = ConceptSchemeTitle.objects.create(
					concept_scheme=concept_scheme, name=other.get("label"),
					language=other.get("lang", "en")
				)
				cs_title.save()
		else:
			pass

		for concept in concept_scheme_has_concepts:
			concept_legacy_id = concept.get("legacy_id")
			concept_inscheme = concept.get("scheme")
			concept_notation = concept.get("notation", "")
			concept_creator = concept.get("creator", "")
			concept_contributor = concept.get("contributor", "")
			concept_alt_labels = concept.get("alt_label")
			concept_hidden_labels = concept.get("hidden_label")
			concept_notes = concept.get("note")
			main_pref_label = {}
			other_pref_labels = []
			for pref_label in concept.get("pref_label"):								
				if  pref_label.get("lang") == self.language:
					main_pref_label["label"] = pref_label.get("label")
					main_pref_label["lang"] = pref_label.get("lang")
				else:
					other_pref_label = {}
					other_pref_label["label"] = pref_label.get("label")
					other_pref_label["lang"] = pref_label.get("lang") 
					other_pref_labels.append(other_pref_label)
			concept_pref_label = main_pref_label.get("label", "no label in this language")
			concept_pref_label_lang = main_pref_label.get("lang", self.language)
			new_concept = SkosConcept.objects.create(
				legacy_id=concept_legacy_id,
				scheme=SkosConceptScheme.objects.get(identifier=concept_inscheme),
				pref_label=concept_pref_label, pref_label_lang=concept_pref_label_lang,
				notation=concept_notation, creator=concept_creator,
				contributor=concept_contributor, created_by=User.objects.get(username='kzaytseva')
				)
			new_concept.save()
			if len(other_pref_labels) > 0:
				for other in other_pref_labels:
					other_label = ConceptLabel.objects.create(
						concept=new_concept, name=other.get("label"),
						language=other.get("lang"), label_type="prefLabel"
						)
					other_label.save()
			else:
				pass
			if  len(concept_alt_labels) > 0:
				for alt in concept_alt_labels:
					alt_label = ConceptLabel.objects.create(
						concept=new_concept, name=alt.get("label"),
						language=alt.get("lang"), label_type="altLabel"
						)
					alt_label.save()
			else:
				pass
			if  len(concept_hidden_labels) > 0:
				for hid in concept_hidden_labels:
					hidden_label = ConceptLabel.objects.create(
						concept=new_concept, name=hid.get("label"),
						language=hid.get("lang"), label_type="hiddenLabel"
					)
					hidden_label.save()
			else:
				pass
			if len(concept_notes) > 0:
				for anynote in concept_notes:
					note = ConceptNote.objects.create(
						concept=new_concept, name=anynote.get("name"),
						language=anynote.get("lang"), note_type=anynote.get("note_type")
						)
					note.save()
			else:
				pass
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

