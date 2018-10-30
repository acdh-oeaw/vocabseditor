from django.conf.urls import url
from . import views
from . import dal_views
from .models import SkosLabel, SkosConcept, SkosConceptScheme, Metadata

app_name = 'vocabs'


urlpatterns = [
    url(r'^$', views.SkosConceptListView.as_view(), name='skosconcept_list'),
    url(r'^concepts/browse/$', views.SkosConceptListView.as_view(), name='browse_vocabs'),
    url(r'^(?P<pk>[0-9]+)$', views.SkosConceptDetailView.as_view(), name='skosconcept_detail'),
    url(r'^create/$', views.SkosConceptCreate.as_view(), name='skosconcept_create'),
    url(r'^update/(?P<pk>[0-9]+)$', views.SkosConceptUpdate.as_view(), name='skosconcept_update'),
    url(r'^delete/(?P<pk>[0-9]+)$', views.SkosConceptDelete.as_view(), name='skosconcept_delete'),
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
    url(r'^label/$', views.SkosLabelListView.as_view(), name='browse_skoslabels'),
    url(
        r'^label/(?P<pk>[0-9]+)$', views.SkosLabelDetailView.as_view(),
        name='skoslabel_detail'),
    url(
        r'^label/create/$', views.SkosLabelCreate.as_view(),
        name='skoslabel_create'),
    url(
        r'^label/update/(?P<pk>[0-9]+)$', views.SkosLabelUpdate.as_view(),
        name='skoslabel_update'),
    url(
        r'^skoslabel/delete/(?P<pk>[0-9]+)$',
        views.SkosLabelDelete.as_view(),
        name='skoslabel_delete',
    ),
    url(
        r'^vocabs-download/$', views.SkosConceptDL.as_view(),
        name='vocabs-download'),
    url(
        r'^metadata/$', views.MetadataListView.as_view(),
        name='metadata'),
    url(
        r'^metadata/(?P<pk>[0-9]+)$', views.MetadataDetailView.as_view(),
        name='metadata_detail'),
    url(
        r'^metadata/create/$', views.MetadataCreate.as_view(),
        name='metadata_create'),
    url(
        r'^metadata/update/(?P<pk>[0-9]+)$', views.MetadataUpdate.as_view(),
        name='metadata_update'),
    url(
        r'^metadata/delete/(?P<pk>[0-9]+)$', views.MetadataDelete.as_view(),
        name='metadata_delete',
    ),
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
        r'^collection/delete/(?P<pk>[0-9]+)$',views.SkosCollectionDelete.as_view(),
        name='skoscollection_delete',
    ),
]
