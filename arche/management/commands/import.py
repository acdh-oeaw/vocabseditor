import json
import os
from django.conf import settings
from django.core.management import BaseCommand
from arche.helpers import path2cols
from arche.models import *


class Command(BaseCommand):
    # Show this when the user types help
    help = "Imports the content of the repo-file-checker output 'fileType.json'"

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, nargs='?', default='fileList.json')

    # A command must define handle()
    def handle(self, *args, **options):
        path_to_file = os.path.join(settings.BASE_DIR, 'arche', 'data', options['file'])
        self.stdout.write("filepath: {}".format(path_to_file))
        data = json.load(open(path_to_file, "r", encoding="utf-8"))
        for x in data:
            filename = x['filename']
            directory = x['directory']
            file_type = x['type']
            size = x['size']
            valid = x['valid_file']
            new_cols = path2cols(directory, '/')
            res, _ = Resource.objects.get_or_create(
                has_title=filename, has_filetype=file_type, file_size=size
            )
            try:
                res.part_of = new_cols[0]
            except:
                pass
            res.save()
            try:
                self.stdout.write("saved: {}".format(res.has_title))
            except:
                pass
        number_of_res = Resource.objects.all().count()
        self.stdout.write("There are {} Resources".format(number_of_res))
