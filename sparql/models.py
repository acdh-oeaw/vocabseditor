import os
from SPARQLWrapper import SPARQLWrapper, JSON
from django.conf import settings
from django.db import models

try:
    endpoint = settings.SPARQL_ENDPOINT
except AttributeError:
    endpoint = 'https://bg{}.acdh.oeaw.ac.at/sparql'.format(
        os.path.basename(settings.BASE_DIR)
    )


class SparqlConfig(models.Model):
    """Stores the URL of a SPARQL-Endpoint"""
    endpoint = models.CharField(default=endpoint, max_length=100)

    def __str__(self):
        return "{}".format(self.endpoint)


class Query(models.Model):
    """Stores sparql-queries"""
    endpoint = models.ForeignKey(
        SparqlConfig, blank=True, null=True, on_delete=models.PROTECT
    )
    query = models.TextField(blank=True, null=True)
    title = models.CharField(default="An example Query", max_length=200)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.endpoint is None:
            temp_endpoint, _ = SparqlConfig.objects.get_or_create(endpoint=endpoint)
            self.endpoint = temp_endpoint
        else:
            pass
        super(Query, self).save(*args, **kwargs)

    def get_rdf(self, *args, **kwargs):
        sparql = SPARQLWrapper(self.endpoint.endpoint)
        sparql.setQuery(self.query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return results['bindings']

    def __str__(self):
        return "{}".format(self.title)
