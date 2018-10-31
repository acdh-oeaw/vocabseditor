from django.contrib import admin
from .models import *

admin.site.register(Metadata)
admin.site.register(SkosLabel)
admin.site.register(SkosConcept)
admin.site.register(SkosCollection)
admin.site.register(SkosConceptScheme)
admin.site.register(SkosNamespace)


# @admin.register(SkosConceptScheme)
# class SkosConceptSchemeAdmin(admin.ModelAdmin):

# 	def save_model(self, request, obj, form, change):
# 		obj.user_manager = request.user
# 		super().save_model(request, obj, form, change)