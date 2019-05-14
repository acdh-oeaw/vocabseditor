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
import logging
from django.core.exceptions import ObjectDoesNotExist

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
		def allowProperties(_property):
			"""Allow DC and DCT properties"""
			properties = [URIRef('http://purl.org/dc/terms/{}'.format(_property)),
				URIRef('http://purl.org/dc/elements/1.1/{}'.format(_property))]
			return properties
		if (None, RDF.type, SKOS.ConceptScheme) in g:
			for cs in g.subjects(RDF.type, SKOS.ConceptScheme):
				concept_scheme["identifier"] = str(cs)
				titles = []
				# set labels properties to recognize all possible labels
				for title in g.preferredLabel(cs, labelProperties=((DC.title), (RDFS.label), (DCT.title), (SKOS.prefLabel))):
					temp_title = {}
					temp_title["title"] = str(title[1])
					# if language attribute is absent populate it with a specified language
					if str(title[1].language) == "None":
						temp_title["lang"] = self.language						
					else:
						temp_title["lang"] = str(title[1].language)
					titles.append(temp_title)
				concept_scheme["title"] = titles
				concept_scheme["creator"] = ";".join([c for cp in allowProperties('creator') for c in g.objects(cs, cp)])
				concept_scheme["contributor"] = ";".join([contr for contrp in allowProperties('contributor') for contr in g.objects(cs, contrp)])
				concept_scheme["language"] = ";".join([l for lp in allowProperties('language') for l in g.objects(cs, lp)])
				concept_scheme["subject"] = ";".join([s for sp in allowProperties('subject') for s in g.objects(cs, sp)])
				concept_scheme["publisher"] = ";".join([p for pp in allowProperties('publisher') for p in g.objects(cs, pp)])
				for license in g.objects(cs, DCT.license):
					concept_scheme["license"] = str(license)
		else:
			raise Exception("rdf:type skos:ConceptScheme is not found")

		logging.info("Concept Scheme: {}".format(concept_scheme))
		# parsing concepts triples
		if (None, RDF.type, SKOS.Concept) in g:
			concepts = []
			for c in g.subjects(RDF.type, SKOS.Concept):
				concept = {}
				concept["legacy_id"] = str(c)
				# pref labels
				pref_labels = []
				for pref_label in g.preferredLabel(c):
					label = {}
					label["label"] = str(pref_label[1])
					if str(pref_label[1].language) == "None":
						label["lang"] = self.language
					else:
						label["lang"] = str(pref_label[1].language)
					pref_labels.append(label)
				concept["pref_label"] = pref_labels
				for scheme in g.objects(c, SKOS.inScheme):
					concept["scheme"] = str(scheme)
				for notation in g.objects(c, SKOS.notation):
					concept["notation"] = str(notation)
				concept["creator"] = ";".join([cr for cr in g.objects(c, DC.creator)])
				concept["contributor"] = ";".join([contr for contr in g.objects(c, DC.contributor)])
				for broader_concept in g.objects(c, SKOS.broader):
					concept["broader_concept"] = str(broader_concept)
				# alt labels
				alt_labels = [] 
				for alt_label in g.objects(c, SKOS.altLabel):
					label = {}
					label["label"] = str(alt_label)
					if str(alt_label.language) == "None":
						label["lang"] = self.language
					else:
						label["lang"] = alt_label.language
					alt_labels.append(label)
				concept["alt_label"] = alt_labels
				# hidden labels
				hidden_labels = [] 
				for hidden_label in g.objects(c, SKOS.hiddenLabel):
					label = {}
					label["label"] = str(hidden_label)
					if str(hidden_label.language) == "None":
						label["lang"] = self.language
					else:
						label["lang"] = hidden_label.language
					hidden_labels.append(label)
				concept["hidden_label"] = hidden_labels
				# sources
				sources = [] 
				for source in g.objects(c, DC.source):
					temp_source = {}
					temp_source["name"] = str(source)
					if str(source.language) == "None":
						temp_source["lang"] = self.language
					else:
						temp_source["lang"] = source.language
					sources.append(temp_source)
				concept["source"] = sources
				# documentary notes
				notes = []
				predicates = [SKOS.note, SKOS.definition, SKOS.scopeNote, SKOS.changeNote,
							 SKOS.editorialNote, SKOS.historyNote, SKOS.example]
				for pred in predicates:
					for note in g.objects(c, pred):
						temp_note = {}
						temp_note["name"] = str(note)
						if str(note.language) == "None":
							temp_note["lang"] = self.language
						else:
							temp_note["lang"] = note.language
						temp_note["note_type"] = re.search('http.*#(.*)', str(pred)).group(1)
						notes.append(temp_note)
				concept["note"] = notes
				# Add concept to a list
				concepts.append(concept)
			concept_scheme["has_concepts"] = concepts
		else:
			pass
			logging.info("Graph doesn't have concepts")
		return concept_scheme


	def upload_data(self, user):
		"""
		Creates and saves concept scheme and its concepts in a database
		"""
		concept_scheme = self.parse_triples()
		concept_scheme_uri = concept_scheme.get("identifier")
		concept_scheme_creator = concept_scheme.get("creator", "")
		concept_scheme_contributor = concept_scheme.get("contributor", "")
		concept_scheme_language = concept_scheme.get("language", "")
		concept_scheme_subject = concept_scheme.get("subject", "")
		concept_scheme_publisher = concept_scheme.get("publisher", "")
		concept_scheme_license = concept_scheme.get("license", "")
		concept_scheme_has_concepts = concept_scheme.get("has_concepts")
		main_title = {}
		other_titles = []
		for title in concept_scheme.get("title"):
			if title.get("lang") == self.language:
				main_title["label"] = title.get("title")
				main_title["lang"] = title.get("lang")
			else:
				other_title = {}
				other_title["label"] = title.get("title", "Empty title")
				other_title["lang"] = title.get("lang", self.language) 
				other_titles.append(other_title)
		concept_scheme_title = main_title.get("label", "No title in specified language")
		concept_scheme_title_lang = main_title.get("lang", self.language)
		concept_scheme = SkosConceptScheme.objects.create(
			identifier=concept_scheme_uri,
			title=concept_scheme_title, title_lang=concept_scheme_title_lang,
			creator=concept_scheme_creator, contributor=concept_scheme_contributor,
			language=concept_scheme_language, subject=concept_scheme_subject,
			publisher=concept_scheme_publisher, license=concept_scheme_license,
			created_by=User.objects.get(username=user)
			)
		concept_scheme.save()
		if  len(other_titles) > 0:
			for other in other_titles:
				cs_title = ConceptSchemeTitle.objects.create(
					concept_scheme=concept_scheme, name=other.get("label"),
					language=other.get("lang")
				)
				cs_title.save()
		else:
			pass

		if concept_scheme_has_concepts:

			for concept in concept_scheme_has_concepts:
				concept_legacy_id = concept.get("legacy_id")
				concept_inscheme = concept.get("scheme")
				concept_notation = concept.get("notation", "")
				concept_creator = concept.get("creator", "")
				concept_contributor = concept.get("contributor", "")
				concept_alt_labels = concept.get("alt_label")
				concept_hidden_labels = concept.get("hidden_label")
				concept_notes = concept.get("note")
				concept_sources = concept.get("source")
				main_pref_label = {}
				other_pref_labels = []
				for pref_label in concept.get("pref_label"):								
					if  pref_label.get("lang") == self.language:
						main_pref_label["label"] = pref_label.get("label")
						main_pref_label["lang"] = pref_label.get("lang")
					else:
						other_pref_label = {}
						other_pref_label["label"] = pref_label.get("label")
						other_pref_label["lang"] = pref_label.get("lang", self.language) 
						other_pref_labels.append(other_pref_label)
				concept_pref_label = main_pref_label.get("label", "no label in this language")
				concept_pref_label_lang = main_pref_label.get("lang", self.language)
				new_concept = SkosConcept.objects.create(
					legacy_id=concept_legacy_id,
					scheme=SkosConceptScheme.objects.get(id=concept_scheme.id),
					pref_label=concept_pref_label, pref_label_lang=concept_pref_label_lang,
					notation=concept_notation, creator=concept_creator,
					contributor=concept_contributor, created_by=User.objects.get(username=user)
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
					for n in concept_notes:
						note = ConceptNote.objects.create(
							concept=new_concept, name=n.get("name"),
							language=n.get("lang"), note_type=n.get("note_type")
							)
						note.save()
				else:
					pass
				if len(concept_sources) > 0:
					for s in concept_sources:
						source = ConceptSource.objects.create(
							concept=new_concept, name=s.get("name"),
							language=s.get("lang")
							)
						source.save()
				else:
					pass
			# add relationships
			for concept in concept_scheme_has_concepts:
				if concept.get("broader_concept") is not None:
					local_concepts = SkosConcept.objects.filter(scheme=concept_scheme.id)
					try:
						update_concept = local_concepts.filter(
							legacy_id=concept.get("legacy_id")).update(
							broader_concept=local_concepts.get(legacy_id=concept.get("broader_concept"))
							)
					except ObjectDoesNotExist as e:
						pass
						logging.info(e)
				else:
					pass
			return SkosConcept.objects.rebuild()
		else:
			pass
		return concept_scheme

