from django.urls import path
from . import dal_views
from .models import SkosConcept, SkosConceptScheme, SkosCollection
from django.contrib.auth.models import User


app_name = "vocabs"

urlpatterns = [
    path(
        "external-link-ac/",
        dal_views.ExternalLinkAC.as_view(),
        name="external-link-ac",
    ),
    path(
        "skosconceptscheme-autocomplete/",
        dal_views.SkosConceptSchemeAC.as_view(model=SkosConceptScheme),
        name="skosconceptscheme-autocomplete",
    ),
    path(
        "skoscollection-autocomplete/",
        dal_views.SkosCollectionAC.as_view(model=SkosCollection),
        name="skoscollection-autocomplete",
    ),
    path(
        "skosconcept-autocomplete/",
        dal_views.SkosConceptAC.as_view(model=SkosConcept),
        name="skosconcept-autocomplete",
    ),
    path(
        "skosconcept-extmatch-autocomplete/",
        dal_views.SkosConceptExternalMatchAC.as_view(model=SkosConcept),
        name="skosconcept-extmatch-autocomplete",
    ),
    path(
        "user-autocomplete/",
        dal_views.UserAC.as_view(model=User),
        name="user-autocomplete",
    ),
]
