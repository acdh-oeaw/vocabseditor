from email.policy import default
from django.core.management.base import BaseCommand
from vocabs.rdf_utils import graph_construct_qs
from vocabs.models import SkosConcept, SkosConceptScheme


class Command(BaseCommand):

	help = 'Dumps the specified SKOSConceptScheme to file'

	def add_arguments(self, parser):
		parser.add_argument(
            '--scheme-id',
			type=int,
            default=1,
            help='SKOSConceptScheme-ID'
        )
		parser.add_argument(
            '--format',
            default="ttl",
            help='The format of SKOS file: accepts only one of the two options - rdf (for xml) or ttl',
        )
		parser.add_argument(
            '--filename',
            default="dump",
            help='Name of the created file; default to "dump"',
        )


	def handle(self, *args, **kwargs):
		"""E.g. command: python manage.py import_skos_vocab test.ttl en ttl username"""
		scheme_id = kwargs['scheme_id']
		export_format = kwargs['format']
		file_name_part = kwargs['filename']
		try:
			scheme = SkosConceptScheme.objects.get(id=scheme_id)
		except Exception as e:
			self.stdout.write(self.style.ERROR(
				f'Following Error occured: {e}'
				)
			)
			return None
		qs = SkosConcept.objects.filter(scheme=scheme)
		self.stdout.write(
			f"found {qs.count()} SkosConcepts for SkosConceptScheme >>{scheme}<< with ID: {scheme.id}"
		)
		
		file_name = f"{file_name_part}.{export_format}"
		self.stdout.write(
			f"start writin to {file_name}"
		)
		if export_format == "rdf":
			export_format = "xml" 
		g = graph_construct_qs(qs)
		g.serialize(file_name, format=export_format)
		self.stdout.write(self.style.SUCCESS(
			f'Successfully exported SkosConceptScheme >>{scheme}<< with ID: {scheme.id} to {file_name}')  
		)
