from django.contrib import admin
from browsing.models import BrowsConf


class BrowsConfAdmin(admin.ModelAdmin):
    list_display = [
        'model_name',
        'label',
        'field_path',
    ]


admin.site.register(BrowsConf, BrowsConfAdmin)
