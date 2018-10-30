from rest_framework import viewsets
from rest_framework import pagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
from .filters import SkosConceptFilter
from .api_renderers import RDFRenderer, SKOSRenderer
from rest_framework.settings import api_settings


class LargeResultsSetPagination(pagination.PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 10000


class MetadataViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Metadata.objects.all()
    serializer_class = MetadataSerializer


class SkosLabelViewSet(viewsets.ModelViewSet):

    queryset = SkosLabel.objects.all()
    serializer_class = SkosLabelSerializer


class SkosNamespaceViewSet(viewsets.ModelViewSet):

    queryset = SkosNamespace.objects.all()
    serializer_class = SkosNamespaceSerializer


class SkosConceptSchemeViewSet(viewsets.ModelViewSet):

    queryset = SkosConceptScheme.objects.all()
    serializer_class = SkosConceptSchemeSerializer


class SkosCollectionViewSet(viewsets.ModelViewSet):

    queryset = SkosCollection.objects.all()
    serializer_class = SkosCollectionSerializer


class SkosConceptViewSet(viewsets.ModelViewSet):

    queryset = SkosConcept.objects.all()
    serializer_class = SkosConceptSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = SkosConceptFilter
    pagination_class = LargeResultsSetPagination

    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (RDFRenderer, SKOSRenderer, )