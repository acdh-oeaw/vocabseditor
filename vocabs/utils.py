import os
from django.conf import settings

RDF_FORMATS = {
    "xml": "rdf",
    "n3": "n3",
    "turtle": "ttl",
    "nt": "nt",
    "pretty-xml": "rdf",
    "trix": "trix",
    "trig": "trig",
    "nquads": "nq",
    "json-ld": ".jsonld",
}


def handle_uploaded_file(file):
    file_name = file.name
    full_file_name = os.path.join(
        settings.MEDIA_ROOT,
        'uploads',
        file_name
    )
    with open(full_file_name, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return full_file_name
