from django.core.management.base import BaseCommand, CommandError
from vocabs.skos_import import SkosImporter


class Command(BaseCommand):

	help = 'Imports  the specified SKOS file to database'

	def add_arguments(self, parser):
		parser.add_argument('file', type=str,
			help='The file name to import')
		parser.add_argument('lang', type=str,
			help='The main language of a vocabulary to be imported')
		parser.add_argument('format', type=str,
			help='The format of SKOS file: accepts only one of the two options - rdf or ttl')
		parser.add_argument('user', type=str,
			help='Username')

	def handle(self, *args, **kwargs):
		"""E.g. command: python manage.py import_skos_vocab test.ttl en ttl username"""
		file = kwargs['file']
		lang = kwargs['lang']
		_format = kwargs['format']
		user = kwargs['user']
		skos_vocab = SkosImporter(
			file=file, language=lang, file_format=_format)
		skos_vocab.upload_data(user=user)
		self.stdout.write(self.style.SUCCESS('Successfully imported SKOS vocabulary'))
