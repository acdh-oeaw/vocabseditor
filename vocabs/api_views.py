from rest_framework import viewsets
from rest_framework import pagination
from rest_framework_guardian import filters

from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
from rest_framework.settings import api_settings
from rest_framework.permissions import DjangoObjectPermissions


class LargeResultsSetPagination(pagination.PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 10000


class SkosConceptSchemeViewSet(viewsets.ModelViewSet):
    queryset = SkosConceptScheme.objects.all()
    serializer_class = SkosConceptSchemeSerializer
    permission_classes = (DjangoObjectPermissions, )
    filter_backends = (filters.ObjectPermissionsFilter, )
    pagination_class = LargeResultsSetPagination


class SkosCollectionViewSet(viewsets.ModelViewSet):
    queryset = SkosCollection.objects.all()
    serializer_class = SkosCollectionSerializer
    permission_classes = (DjangoObjectPermissions, )
    filter_backends = (filters.ObjectPermissionsFilter, )
    pagination_class = LargeResultsSetPagination


class SkosConceptViewSet(viewsets.ModelViewSet):
    queryset = SkosConcept.objects.all()
    serializer_class = SkosConceptSerializer
    filter_backends = (DjangoFilterBackend, filters.ObjectPermissionsFilter,)
    pagination_class = LargeResultsSetPagination
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    permission_classes = (DjangoObjectPermissions, )
