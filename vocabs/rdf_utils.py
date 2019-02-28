import rdflib
from rdflib import Graph, Literal, Namespace, RDF, URIRef, RDFS, XSD
from rdflib.namespace import DC, RDFS, SKOS


SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
DC = Namespace("http://purl.org/dc/elements/1.1/")
DCT = Namespace("http://purl.org/dc/terms/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
VOCABS = Namespace("https://vocabs.acdh.oeaw.ac.at/create-concept-scheme/")


def graph_construct_qs(results):
	g = rdflib.Graph()
	g.bind('skos', SKOS)
	g.bind('dc', DC)
	g.bind('dct', DCT)
	g.bind('rdfs', RDFS)
	g.bind('owl', OWL)             
	for obj in results:
		# Creating Main Concept Scheme
		if obj.scheme:
			mainConceptScheme = URIRef(obj.scheme.identifier)
			g.add((mainConceptScheme, RDF.type, SKOS.ConceptScheme))
			# Concept Scheme properties
			if obj.scheme.title:
				g.add((mainConceptScheme, DC.title, Literal(obj.scheme.title, lang=obj.scheme.title_lang)))
				g.add((mainConceptScheme, RDFS.label, Literal(obj.scheme.title, lang=obj.scheme.title_lang)))
			if obj.scheme.has_titles.all():
				for title in obj.scheme.has_titles.all():
					g.add((mainConceptScheme, DC.title, Literal(title.name, lang=title.language)))
			if obj.scheme.has_descriptions.all():
				for desc in obj.scheme.has_descriptions.all():
					g.add((mainConceptScheme, DC.description, Literal(desc.name, lang=desc.language)))
			if obj.scheme.has_sources.all():
				for source in obj.scheme.has_sources.all():
					g.add((mainConceptScheme, DC.source, Literal(source.name, lang=source.language)))
			# accessing lists with ; in TextField
			if obj.scheme.creator:
				for i in obj.scheme.creator.split(';'):              
					g.add((mainConceptScheme, DC.creator, Literal(i.strip())))
			if obj.scheme.contributor:
				for i in obj.scheme.contributor.split(';'):              
					g.add((mainConceptScheme, DC.contributor, Literal(i.strip())))
			if obj.scheme.language:
				for i in obj.scheme.language.split(';'):             
					g.add((mainConceptScheme, DC.language, Literal(i.strip())))
			if obj.scheme.subject:
				for i in obj.scheme.subject.split(';'):              
					g.add((mainConceptScheme, DC.subject, Literal(i.strip())))
			if obj.scheme.coverage:
				for i in obj.scheme.coverage.split(';'):              
					g.add((mainConceptScheme, DC.coverage, Literal(i.strip())))
		# the rest of the properties
			if obj.scheme.license:
				g.add((mainConceptScheme, DCT.license, Literal(obj.scheme.license)))
			if obj.scheme.version:
				g.add((mainConceptScheme, OWL.versionInfo, Literal(obj.scheme.version)))
			if obj.scheme.publisher:
				g.add((mainConceptScheme, DC.publisher, Literal(obj.scheme.publisher)))
			if obj.scheme.relation:
				g.add((mainConceptScheme, DC.relation, URIRef(obj.scheme.relation)))
			if obj.scheme.owner:
				g.add((mainConceptScheme, DCT.rightsHolder, Literal(obj.scheme.owner)))
			g.add((mainConceptScheme, DCT.created, Literal(obj.scheme.date_created, datatype=XSD.dateTime)))
			g.add((mainConceptScheme, DCT.modified, Literal(obj.scheme.date_modified, datatype=XSD.dateTime)))
			if obj.scheme.date_issued:
				g.add((mainConceptScheme, DCT.issued, Literal(obj.scheme.date_issued, datatype=XSD.dateTime)))
			else:
				pass   
		else:
			mainConceptScheme = URIRef(VOCABS)
			g.add((mainConceptScheme, RDF.type, SKOS.ConceptScheme))
		# Concept properties
		concept = URIRef(mainConceptScheme + "#concept" + str(obj.id))
		g.add((concept, RDF.type, SKOS.Concept))
		g.add((concept, SKOS.prefLabel, Literal(obj.pref_label, lang=obj.pref_label_lang)))
		g.add((concept, SKOS.notation, Literal(obj.notation)))
		# each concept must have skos:inScheme mainConceptScheme
		g.add((concept, SKOS.inScheme, mainConceptScheme))
		if obj.collection.all():
			for x in obj.collection.all():
				collection = URIRef(mainConceptScheme + "#collection" + str(x.id))
				g.add((collection, RDF.type, SKOS.Collection))
				g.add((collection, DCT.created, Literal(x.date_created, datatype=XSD.dateTime)))
				g.add((collection, DCT.modified, Literal(x.date_modified, datatype=XSD.dateTime)))
				if x.name:
					g.add((collection, SKOS.prefLabel, Literal(x.name, lang=x.label_lang)))
				# Collection labels
				if x.has_labels.all():
					for label in x.has_labels.all():
						if label.label_type == 'prefLabel':
							g.add((collection, SKOS.prefLabel, Literal(label.name, lang=label.language)))
						elif label.label_type == 'altLabel':
							g.add((collection, SKOS.altLabel, Literal(label.name, lang=label.language)))
						elif label.label_type == 'hiddenLabel':
							g.add((collection, SKOS.hiddenLabel, Literal(label.name, lang=label.language)))
						else:
							g.add((collection, SKOS.altLabel, Literal(label.name, lang=label.language)))
				# Collection notes
				if x.has_notes.all():
					for note in x.has_notes.all():
						if note.note_type == 'note':
							g.add((collection, SKOS.note, Literal(note.name, lang=note.language)))
						elif note.note_type == 'scopeNote':
							g.add((collection, SKOS.scopeNote, Literal(note.name, lang=note.language)))
						elif note.note_type == 'changeNote':
							g.add((collection, SKOS.changeNote, Literal(note.name, lang=note.language)))
						elif note.note_type == 'editorialNote':
							g.add((collection, SKOS.editorialNote, Literal(note.name, lang=note.language)))
						elif note.note_type == 'historyNote':
							g.add((collection, SKOS.historyNote, Literal(note.name, lang=note.language)))
						elif note.note_type == 'definition':
							g.add((collection, SKOS.definition, Literal(note.name, lang=note.language)))
						elif note.note_type == 'example':
							g.add((collection, SKOS.example, Literal(note.name, lang=note.language)))
						else:
							g.add((collection, SKOS.note, Literal(note.name, lang=note.language)))
				# Collection sources
				if x.has_sources.all():
					for source in x.has_sources.all():
						g.add((collection, DC.source, Literal(source.name, lang=source.language)))
				if x.creator:
					for i in x.creator.split(';'):              
						g.add((collection, DC.creator, Literal(i.strip())))
				if x.contributor:
					for i in x.contributor.split(';'):              
						g.add((collection, DC.contributor, Literal(i.strip())))
				if x.has_members.all():
					for y in x.has_members.all():
						g.add((collection, SKOS.member, URIRef(mainConceptScheme + "#concept" + str(y.id))))
		# Concept properties
		if obj.has_labels.all():
			for label in obj.has_labels.all():
				if label.label_type == 'prefLabel':
					g.add((concept, SKOS.prefLabel, Literal(label.name, lang=label.language)))
				elif label.label_type == 'altLabel':
					g.add((concept, SKOS.altLabel, Literal(label.name, lang=label.language)))
				elif label.label_type == 'hiddenLabel':
					g.add((concept, SKOS.hiddenLabel, Literal(label.name, lang=label.language)))
				# if label.label_type is not set then make it altLabel
				else:
					g.add((concept, SKOS.altLabel, Literal(label.name, lang=label.language)))
		if obj.has_notes.all():
			for note in obj.has_notes.all():
				if note.note_type == 'note':
					g.add((concept, SKOS.note, Literal(note.name, lang=note.language)))
				elif note.note_type == 'scopeNote':
					g.add((concept, SKOS.scopeNote, Literal(note.name, lang=note.language)))
				elif note.note_type == 'changeNote':
					g.add((concept, SKOS.changeNote, Literal(note.name, lang=note.language)))
				elif note.note_type == 'editorialNote':
					g.add((concept, SKOS.editorialNote, Literal(note.name, lang=note.language)))
				elif note.note_type == 'historyNote':
					g.add((concept, SKOS.historyNote, Literal(note.name, lang=note.language)))
				elif note.note_type == 'definition':
					g.add((concept, SKOS.definition, Literal(note.name, lang=note.language)))
				elif note.note_type == 'example':
					g.add((concept, SKOS.example, Literal(note.name, lang=note.language)))
				else:
					g.add((concept, SKOS.note, Literal(note.name, lang=note.language)))
		if obj.has_sources.all():
			for source in obj.has_sources.all():
				g.add((concept, DC.source, Literal(source.name, lang=source.language)))
		#top concepts
		# if obj.top_concept == True:
		if not obj.broader_concept:
			g.add((mainConceptScheme, SKOS.hasTopConcept, URIRef(concept)))
			g.add((concept, SKOS.topConceptOf, mainConceptScheme ))
		# modelling broader/narrower relationships
		if obj.broader_concept:
			g.add((concept, SKOS.broader, URIRef(mainConceptScheme + "#concept"+ str(obj.broader_concept.id))))
		if obj.narrower_concepts.all():
			#g.add((mainConceptScheme, SKOS.hasTopConcept, URIRef(concept)))
			#g.add((concept, SKOS.topConceptOf, mainConceptScheme ))
			for x in obj.narrower_concepts.all():
				g.add((concept, SKOS.narrower, URIRef(mainConceptScheme + "#concept" + str(x.id))))
		# modelling matches
		if obj.skos_related.all():
			for x in obj.skos_related.all():
				g.add((concept, SKOS.related, URIRef(x.scheme.identifier + "#concept" + str(x.id))))
		if obj.related.all():
			for x in obj.related.all():
				g.add((concept, SKOS.related, URIRef(x.scheme.identifier + "#concept" + str(x.id))))
		#############################################################################################
		#       external matches should use external CS URI for construsting their own URIs         #

		if obj.skos_broadmatch.all():
			for x in obj.skos_broadmatch.all():
				g.add((concept, SKOS.broadMatch, URIRef(x.scheme.identifier + "#concept" + str(x.id))))
		if obj.narrowmatch.all():
			for x in obj.narrowmatch.all():
				g.add((concept, SKOS.narrowMatch, URIRef(x.scheme.identifier + "#concept" + str(x.id))))
		if obj.skos_narrowmatch.all():
			for x in obj.skos_narrowmatch.all():
				g.add((concept, SKOS.narrowMatch, URIRef(x.scheme.identifier + "#concept" + str(x.id))))
		if obj.broadmatch.all():
			for x in obj.broadmatch.all():
				g.add((concept, SKOS.broadMatch, URIRef(x.scheme.identifier + "#concept" + str(x.id))))
		if obj.skos_exactmatch.all():
			for x in obj.skos_exactmatch.all():
				g.add((concept, SKOS.exactMatch, URIRef(x.scheme.identifier + "#concept" + str(x.id))))
		if obj.exactmatch.all():
			for x in obj.exactmatch.all():
				g.add((concept, SKOS.exactMatch, URIRef(x.scheme.identifier + "#concept" + str(x.id))))
		if obj.skos_relatedmatch.all():
			for x in obj.skos_relatedmatch.all():
				g.add((concept, SKOS.relatedMatch, URIRef(x.scheme.identifier + "#concept" + str(x.id))))
		if obj.relatedmatch.all():
			for x in obj.relatedmatch.all():
				g.add((concept, SKOS.relatedMatch, URIRef(x.scheme.identifier + "#concept" + str(x.id))))
		if obj.skos_closematch.all():
			for x in obj.skos_closematch.all():
				g.add((concept, SKOS.closeMatch, URIRef(x.scheme.identifier + "#concept" + str(x.id))))
		if obj.closematch.all():
			for x in obj.closematch.all():
				g.add((concept, SKOS.closeMatch, URIRef(x.scheme.identifier + "#concept" + str(x.id))))

		#############################################################################################
		if obj.same_as_external:
			for i in obj.same_as_external.split(';'):
				g.add((concept, OWL.sameAs, URIRef(i.strip())))
		if obj.creator:
			for i in obj.creator.split(';'):
				g.add((concept, DC.creator, Literal(i.strip())))
		if obj.contributor:
			for i in obj.contributor.split(';'):
				g.add((concept, DC.contributor, Literal(i.strip())))
		if obj.date_created:
			g.add((concept, DCT.created, Literal(obj.date_created, datatype=XSD.dateTime)))
		if obj.date_modified:
			g.add((concept, DCT.modified, Literal(obj.date_modified, datatype=XSD.dateTime)))
	return g
