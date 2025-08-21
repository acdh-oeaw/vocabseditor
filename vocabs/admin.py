from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from mptt.admin import MPTTModelAdmin
from reversion.admin import VersionAdmin

from .models import (
    CollectionLabel,
    CollectionNote,
    CollectionSource,
    ConceptLabel,
    ConceptNote,
    ConceptSchemeDescription,
    ConceptSchemeSource,
    ConceptSchemeTitle,
    ConceptSource,
    CustomProperty,
    SkosCollection,
    SkosConcept,
    SkosConceptScheme,
)


# With object permissions support
@admin.register(SkosConcept)
class SkosConceptAdmin(MPTTModelAdmin, GuardedModelAdmin, VersionAdmin):
    pass


class SkosCollectionAdmin(GuardedModelAdmin, VersionAdmin):
    pass


class SkosConceptSchemeAdmin(GuardedModelAdmin, VersionAdmin):
    pass


admin.site.register(SkosCollection, SkosCollectionAdmin)
admin.site.register(SkosConceptScheme, SkosConceptSchemeAdmin)
admin.site.register(ConceptSchemeTitle)
admin.site.register(ConceptSchemeDescription)
admin.site.register(ConceptSchemeSource)
admin.site.register(CollectionLabel)
admin.site.register(CollectionNote)
admin.site.register(CollectionSource)
admin.site.register(ConceptLabel)
admin.site.register(ConceptNote)
admin.site.register(ConceptSource)
admin.site.register(CustomProperty)
