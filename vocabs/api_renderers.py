from rest_framework import renderers
from django.template.loader import render_to_string
import rdflib
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef, RDFS, ConjunctiveGraph, XSD
from rdflib.namespace import DC, FOAF, RDFS, SKOS
from .models import *
from django.core.exceptions import ValidationError
from .rdf_utils import *


class RDFRenderer(renderers.BaseRenderer):
	media_type = 'text/xml'
	format = 'xml'

	def render(self, data, media_type=None, renderer_context=None):
		data = render_to_string(
			"vocabs/RDF_renderer.xml", {'data': data, 'renderer_context': renderer_context})

		return data


class SKOSRenderer(renderers.BaseRenderer):
	media_type = 'text/xml'
	format = 'rdf'

	def render(self, data, media_type=None, renderer_context=None):
		if 'results' in data:
			g = graph_construct(data['results'])
		else:
			g = graph_construct([data])
		result = g.serialize(format="pretty-xml")
		return result