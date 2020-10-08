from django.conf.urls import url
from . import views


app_name = 'vocabs'

urlpatterns = [
    url(r'^concepts/$', views.SkosConceptListView.as_view(), name='browse_vocabs'),
    url(r'^concepts/(?P<pk>[0-9]+)$', views.SkosConceptDetailView.as_view(), name='skosconcept_detail'),
    url(r'^concepts/create/$', views.SkosConceptCreate.as_view(), name='skosconcept_create'),
    url(r'^concepts/update/(?P<pk>[0-9]+)$', views.SkosConceptUpdate.as_view(), name='skosconcept_update'),
    url(r'^concepts/delete/(?P<pk>[0-9]+)$', views.SkosConceptDelete.as_view(), name='skosconcept_delete'),
    url(r'^scheme/$', views.SkosConceptSchemeListView.as_view(), name='browse_schemes'),
    url(
        r'^scheme/(?P<pk>[0-9]+)$', views.SkosConceptSchemeDetailView.as_view(),
        name='skosconceptscheme_detail'),
    url(
        r'^scheme/create/$', views.SkosConceptSchemeCreate.as_view(),
        name='skosconceptscheme_create'),
    url(
        r'^scheme/update/(?P<pk>[0-9]+)$', views.SkosConceptSchemeUpdate.as_view(),
        name='skosconceptscheme_update'),
    url(
        r'^scheme/delete/(?P<pk>[0-9]+)$',
        views.SkosConceptSchemeDelete.as_view(),
        name='skosconceptscheme_delete',
    ),
    url(
        r'^vocabs-download/$', views.SkosConceptDL.as_view(),
        name='vocabs-download'),
    url(
        r'^collection/$', views.SkosCollectionListView.as_view(),
        name='browse_skoscollections'),
    url(
        r'^collection/(?P<pk>[0-9]+)$', views.SkosCollectionDetailView.as_view(),
        name='skoscollection_detail'),
    url(
        r'^collection/create/$', views.SkosCollectionCreate.as_view(),
        name='skoscollection_create'),
    url(
        r'^collection/update/(?P<pk>[0-9]+)$', views.SkosCollectionUpdate.as_view(),
        name='skoscollection_update'),
    url(
        r'^collection/delete/(?P<pk>[0-9]+)$', views.SkosCollectionDelete.as_view(),
        name='skoscollection_delete',
    ),
    url(r'^import/$', views.file_upload, name='import'),
]
