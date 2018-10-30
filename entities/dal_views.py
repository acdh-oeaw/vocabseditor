from dal import autocomplete
from .models import *
from django.db.models import Q


class AlternativeNameAC(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = AlternativeName.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class PlaceAC(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Place.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class PersonAC(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Person.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class InstitutionAC(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Institution.objects.all()

        if self.q:
            qs = qs.filter(written_name__icontains=self.q)

        return qs
