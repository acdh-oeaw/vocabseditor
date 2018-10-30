from django.conf.urls import url, include, handler404
from django.contrib import admin
from django.conf import settings
from rest_framework import routers
# from entities.apis_views import PlaceViewSet, GeoJsonViewSet
from vocabs import api_views

if 'bib' in settings.INSTALLED_APPS:
    from bib.api_views import ZotItemViewSet



router = routers.DefaultRouter()
# router.register(r'geojson', GeoJsonViewSet, base_name='places')
router.register(r'metadata', api_views.MetadataViewSet)
router.register(r'skoslabels', api_views.SkosLabelViewSet)
router.register(r'skosnamespaces', api_views.SkosNamespaceViewSet)
router.register(r'skosconceptschemes', api_views.SkosConceptSchemeViewSet)
router.register(r'skoscollections', api_views.SkosCollectionViewSet)
router.register(r'skosconcepts', api_views.SkosConceptViewSet)
# router.register(r'places', PlaceViewSet)
if 'bib' in settings.INSTALLED_APPS:
    router.register(r'zotitems', ZotItemViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
    # url(r'^arche/', include('arche.urls', namespace='arche')),
    url(r'^sparql/', include('sparql.urls', namespace='sparql')),
    url(r'^vocabs/', include('vocabs.urls', namespace='vocabs')),
    url(r'^vocabs-ac/', include('vocabs.dal_urls', namespace='vocabs-ac')),
    # url(r'^entities-ac/', include('entities.dal_urls', namespace='entities-ac')),
    # url(r'^entities/', include('entities.urls', namespace='entities')),
    url(r'^', include('webpage.urls', namespace='webpage')),
]

if 'bib' in settings.INSTALLED_APPS:
    urlpatterns.append(
        url(r'^bib/', include('bib.urls', namespace='bib')),
    )

handler404 = 'webpage.views.handler404'
