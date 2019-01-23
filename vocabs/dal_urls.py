from django.conf.urls import url
from django.urls import path
from . import views
from . import dal_views
from .models import SkosConcept, SkosConceptScheme, SkosCollection
from django.contrib.auth.models import User

app_name = 'vocabs'

urlpatterns = [
    url(
        r'^skosconceptscheme-autocomplete/$', dal_views.SkosConceptSchemeAC.as_view(
            model=SkosConceptScheme),
        name='skosconceptscheme-autocomplete',
    ),
    url(
        r'^skoscollection-autocomplete/$', dal_views.SkosCollectionAC.as_view(
            model=SkosCollection),
        name='skoscollection-autocomplete',
    ),
    url(
        r'^skosconcept-autocomplete/$', dal_views.SpecificConcepts.as_view(
            model=SkosConcept),
        name='skosconcept-autocomplete',
    ),
    url(
        r'^skosconcept-filter-autocomplete/$', dal_views.SpecificConcepts.as_view(
            model=SkosConcept),
        name='skosconcept-filter-autocomplete',
    ),
    url(
        r'^skosconcept-nobroaderterm-autocomplete/$', dal_views.SkosConceptNoBroaderTermAC.as_view(
            model=SkosConcept),
        name='skosconcept-nobroaderterm-autocomplete',
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
    ),
    url(
        r'^user-autocomplete/$', dal_views.UserAC.as_view(
            model=User),
        name='user-autocomplete',
    ),
]
