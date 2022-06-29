from django.urls import path, include
from django.contrib import admin
from rest_framework import routers, permissions
from vocabs import api_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Vocabs",
      default_version='v1',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register(r'skosconceptschemes', api_views.SkosConceptSchemeViewSet)
router.register(r'skoscollections', api_views.SkosCollectionViewSet)
router.register(r'skosconcepts', api_views.SkosConceptViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(
        'api/schema/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'
    ),
    path('admin/', admin.site.urls),
    path('vocabs/', include('vocabs.urls', namespace='vocabs')),
    path('vocabs-ac/', include('vocabs.dal_urls', namespace='vocabs-ac')),
    path('', include('webpage.urls', namespace='webpage')),
]

handler404 = 'webpage.views.handler404'
