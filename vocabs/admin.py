from django.contrib import admin
from .models import *
from guardian.admin import GuardedModelAdmin


# With object permissions support
class SkosLabelAdmin(GuardedModelAdmin):
    pass


class SkosConceptAdmin(GuardedModelAdmin):
    pass


class SkosCollectionAdmin(GuardedModelAdmin):
    pass


class SkosConceptSchemeAdmin(GuardedModelAdmin):
    pass

admin.site.register(Metadata)
admin.site.register(SkosLabel, SkosLabelAdmin)
admin.site.register(SkosConcept, SkosConceptAdmin)
admin.site.register(SkosCollection, SkosCollectionAdmin)
admin.site.register(SkosConceptScheme, SkosConceptSchemeAdmin)
admin.site.register(SkosNamespace)


# @admin.register(SkosConceptScheme)
# class SkosConceptSchemeAdmin(admin.ModelAdmin):

# 	def save_model(self, request, obj, form, change):
# 		obj.created_by = request.user
# 		super().save_model(request, obj, form, change)