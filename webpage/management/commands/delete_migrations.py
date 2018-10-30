import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

cwd = settings.BASE_DIR


class Command(BaseCommand):
    # Show this when the user types help
    help = "Deletes all migration files of the current project"

    # A command must define handle()
    def handle(self, *args, **options):
        deleted_files = []
        counter = 0
        for root, dirs, files in os.walk(cwd):
            for file in files:
                if 'migrations' in os.path.join(root, file) and '00' in os.path.join(root, file):
                    deleted_files.append((os.path.join(root, file)))
                    os.remove(os.path.join(root, file))
                    counter = +1
        self.stdout.write("Following {} files have been deleted".format(counter))
        for x in deleted_files:
            self.stdout.write("Deleted: {}".format(x))
