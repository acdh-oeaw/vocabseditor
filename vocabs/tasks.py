import os
import glob
from celery import shared_task
from django.conf import settings
from django.utils.text import slugify

from vocabs.models import SkosConceptScheme, SkosConcept
from vocabs.rdf_utils import graph_construct_qs, RDF_FORMATS
from vocabs.skos_import import SkosImporter
from vocabs.utils import push_to_gh


@shared_task(name="Export")
def export_concept_schema(schema_id, export_format):
    schema = SkosConceptScheme.objects.get(id=schema_id)
    qs = SkosConcept.objects.filter(scheme=schema)
    g = graph_construct_qs(qs)
    file_name = f"{slugify(schema.title)}.{RDF_FORMATS[export_format]}"
    export_path = os.path.join(settings.MEDIA_ROOT, file_name)
    g.serialize(export_path, format=export_format)
    os.chmod(export_path, 0o0755)  # this is needed because I don't get docker permission/user things
    commit_message = f"{file_name} exported from vocabseditor"
    files = glob.glob(f"{settings.MEDIA_ROOT}*.*", recursive=False)
    push_to_gh(
        files,
        commit_message=commit_message
    )
    return f"/media/{file_name}"


@shared_task(name="Import")
def import_concept_schema(full_path, user_name, file_format=None, language=None):
    if file_format == 'ttl':
        skos_vocab = SkosImporter(
            file=full_path,
            file_format="ttl",
            language=language
        )
    else:
        skos_vocab = SkosImporter(
            file=full_path,
            language=language
        )
    result = skos_vocab.upload_data(user=user_name)
    return result
