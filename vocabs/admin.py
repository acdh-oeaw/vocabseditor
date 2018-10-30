from django.contrib import admin
from .models import *

admin.site.register(Metadata)
admin.site.register(SkosLabel)
admin.site.register(SkosConcept)
admin.site.register(SkosCollection)
admin.site.register(SkosConceptScheme)
admin.site.register(SkosNamespace)
