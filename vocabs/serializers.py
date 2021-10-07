from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class SkosConceptSchemeSerializer(serializers.ModelSerializer):
    has_concepts = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='skosconcept-detail')
    curator = serializers.StringRelatedField(many=True, required=False)
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username')

    class Meta:
        model = SkosConceptScheme
        fields = '__all__'


class SkosCollectionSerializer(serializers.ModelSerializer):
    has_members = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='skosconcept-detail')
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username')

    class Meta:
        model = SkosCollection
        fields = '__all__'


class SkosConceptSerializer(serializers.ModelSerializer):
    created_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username')

    class Meta:
        model = SkosConcept
        exclude = ["lft", "rght", "tree_id", "level"]
