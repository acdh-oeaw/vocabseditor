from django.conf.urls import url
from django.urls import path
from . import views
from . import dal_views
from .models import SkosLabel, SkosConcept, SkosConceptScheme, SkosCollection

app_name = 'vocabs'

urlpatterns = [
    url(
        r'^skoslabel-autocomplete/$', dal_views.SkosLabelAC.as_view(
            model=SkosLabel, create_field='name',),
        name='skoslabel-autocomplete',
    ),
    url(
        r'^skoslabel-filter-autocomplete/$', dal_views.SkosLabelAC.as_view(
            model=SkosLabel),
        name='skoslabel-filter-autocomplete',
    ),
    url(
        r'^skosconceptscheme-autocomplete/$', dal_views.SkosConceptSchemeAC.as_view(
            model=SkosConceptScheme,
            create_field='dc_title',),
        name='skosconceptscheme-autocomplete',
    ),
    url(
        r'^skoscollection-autocomplete/$', dal_views.SkosCollectionAC.as_view(
            model=SkosCollection,
            create_field='name',),
        name='skoscollection-autocomplete',
    ),
    url(
        r'^skosconcept-autocomplete/$', dal_views.SpecificConcepts.as_view(
            model=SkosConcept,
            create_field='pref_label',),
        name='skosconcept-autocomplete',
    ),
    url(
        r'^skosconcept-filter-autocomplete/$', dal_views.SpecificConcepts.as_view(
            model=SkosConcept),
        name='skosconcept-filter-autocomplete',
    ),
    url(
        r'^skosconcept-pref-label-autocomplete/$',
        dal_views.SkosConceptPrefLabalAC.as_view(),
        name='skosconcept-label-ac',
    ),
    url(
        r'^skos-constraint-ac/$', dal_views.SKOSConstraintAC.as_view(model=SkosConcept),
        name='skos-constraint-ac',
    ),
    url(
        r'^skos-constraint-no-hierarchy-ac/$', dal_views.SKOSConstraintACNoHierarchy.as_view(
            model=SkosConcept),
        name='skos-constraint-no-hierarchy-ac',
    ),
    path(
        r'specific-concept-ac/<str:scheme>', dal_views.SpecificConcepts.as_view(
            model=SkosConcept),
        name='specific-concept-ac',
    )
]
