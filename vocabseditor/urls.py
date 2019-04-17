from django.conf.urls import url, include, handler404
from django.contrib import admin
from django.conf import settings
from rest_framework import routers
from vocabs import api_views
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Vocabseditor API')

router = routers.DefaultRouter()
router.register(r'skosconceptschemes', api_views.SkosConceptSchemeViewSet)
router.register(r'skoscollections', api_views.SkosCollectionViewSet)
router.register(r'skosconcepts', api_views.SkosConceptViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
    url(r'^vocabs/', include('vocabs.urls', namespace='vocabs')),
    url(r'^vocabs-ac/', include('vocabs.dal_urls', namespace='vocabs-ac')),
    url(r'^', include('webpage.urls', namespace='webpage')),
    url(r'^api/schema/', schema_view),
]


handler404 = 'webpage.views.handler404'