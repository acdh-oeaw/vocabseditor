import django_filters
from dal import autocomplete
from .models import *

django_filters.filters.LOOKUP_TYPES = [
    ('', '---------'),
    ('exact', 'Is equal to'),
    ('iexact', 'Is equal to (case insensitive)'),
    ('not_exact', 'Is not equal to'),
    ('lt', 'Lesser than/before'),
    ('gt', 'Greater than/after'),
    ('gte', 'Greater than or equal to'),
    ('lte', 'Lesser than or equal to'),
    ('startswith', 'Starts with'),
    ('endswith', 'Ends with'),
    ('contains', 'Contains'),
    ('icontains', 'Contains (case insensitive)'),
    ('not_contains', 'Does not contain'),
]


class ResourceListFilter(django_filters.FilterSet):
    has_title = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text=Resource._meta.get_field('has_title').help_text,
        label=Resource._meta.get_field('has_title').verbose_name
        )
    description = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text=Resource._meta.get_field('description').help_text,
        label=Resource._meta.get_field('description').verbose_name
        )
    part_of = django_filters.ModelMultipleChoiceFilter(
        queryset=Collection.objects.all(),
        help_text=Resource._meta.get_field('part_of').help_text,
        label=Resource._meta.get_field('part_of').verbose_name
        )

    class Meta:
        model = Resource
        fields = "__all__"


class ProjectListFilter(django_filters.FilterSet):
    has_title = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text=Project._meta.get_field('has_title').help_text,
        label=Project._meta.get_field('has_title').verbose_name
        )
    description = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text=Project._meta.get_field('description').help_text,
        label=Project._meta.get_field('description').verbose_name
        )

    class Meta:
        model = Project
        fields = "__all__"


class CollectionListFilter(django_filters.FilterSet):
    has_title = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text=Collection._meta.get_field('has_title').help_text,
        label=Collection._meta.get_field('has_title').verbose_name
        )
    description = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text=Collection._meta.get_field('description').help_text,
        label=Collection._meta.get_field('description').verbose_name
        )

    class Meta:
        model = Collection
        fields = "__all__"
