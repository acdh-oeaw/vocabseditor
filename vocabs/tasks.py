import os
from celery import shared_task
from django.conf import settings
from django.utils.text import slugify

from vocabs.rdf_utils import graph_construct_qs, RDF_FORMATS
from vocabs.models import SkosConceptScheme, SkosConcept


@shared_task
def export_concept_schema(schema_id, export_format):
    schema = SkosConceptScheme.objects.get(id=schema_id)
    qs = SkosConcept.objects.filter(scheme=schema)
    g = graph_construct_qs(qs)
    file_name = f"{slugify(schema.title)}.{RDF_FORMATS[export_format]}"
    export_path = os.path.join(settings.MEDIA_ROOT, file_name)
    g.serialize(export_path, format=export_format)
    os.chmod(export_path, 0o0755)  # this is needed because I don't get docker permission/user things
    return file_name
