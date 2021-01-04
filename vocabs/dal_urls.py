from django.conf.urls import url
from . import dal_views
from .models import SkosConcept, SkosConceptScheme, SkosCollection
from django.contrib.auth.models import User


app_name = 'vocabs'

urlpatterns = [
    url(
        r'^external-link-ac/$', dal_views.ExternalLinkAC.as_view(),
        name='external-link-ac',
    ),
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
        r'^skosconcept-autocomplete/$', dal_views.SkosConceptAC.as_view(
            model=SkosConcept),
        name='skosconcept-autocomplete',
    ),
    url(
        r'^skosconcept-extmatch-autocomplete/$', dal_views.SkosConceptExternalMatchAC.as_view(
            model=SkosConcept),
        name='skosconcept-extmatch-autocomplete',
    ),
    url(
        r'^user-autocomplete/$', dal_views.UserAC.as_view(
            model=User),
        name='user-autocomplete',
    ),
]
