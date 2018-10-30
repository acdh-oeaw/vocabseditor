from django.core.management.base import BaseCommand, CommandError

from browsing.models import BrowsConf


class Command(BaseCommand):

    help = "Delete all BrowsConf objects"

    def handle(self, *args, **options):
        brc_objs = BrowsConf.objects.all()
        self.stdout.write("{} objects will be deleted".format(brc_objs.count()))
        brc_objs.delete()
        self.stdout.write("All BrowsConf objects are gone")
