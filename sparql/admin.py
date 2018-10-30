from django.contrib import admin
from .models import Query, SparqlConfig

admin.site.register(Query)
admin.site.register(SparqlConfig)

# Register your models here.
