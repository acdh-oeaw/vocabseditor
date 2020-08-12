from rest_framework import serializers
from .models import *


class SkosConceptSchemeSerializer(serializers.HyperlinkedModelSerializer):
    has_concepts = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='skosconcept-detail')
    created_by = serializers.CharField(read_only=True)
    curator = serializers.StringRelatedField(many=True)

    class Meta:
        model = SkosConceptScheme
        fields = '__all__'


class SkosCollectionSerializer(serializers.HyperlinkedModelSerializer):
    has_members = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='skosconcept-detail')
    created_by = serializers.CharField(read_only=True)

    class Meta:
        model = SkosCollection
        fields = '__all__'


class SkosConceptSerializer(serializers.HyperlinkedModelSerializer):
    created_by = serializers.CharField(read_only=True)

    class Meta:
        model = SkosConcept
        fields = (
            'id', 'url',
            'pref_label', 'pref_label_lang',
            'scheme', 'collection',
            'broader_concept', 'narrower_concepts',
            'notation', 'related',
            'broad_match', 'narrow_match',
            'exact_match', 'related_match',
            'close_match', 'legacy_id',
            'creator', 'contributor',
            'date_created', 'date_modified',
            'created_by',
        )
