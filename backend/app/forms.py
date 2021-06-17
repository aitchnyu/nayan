from django import forms
from django.contrib.gis import geos
from django.forms import ValidationError

from . import models


class CoordinatesField(forms.Field):
    def clean(self, value: str):
        try:
            raw_latitude, raw_longitude = value.split(",")
            latitude = float(raw_latitude)
            longitude = float(raw_longitude)
        except ValueError:  # Cant split, cant parse
            raise ValidationError("Malformed Location")
        if latitude < 0 or latitude > 90 or longitude < -180 or longitude > 180:
            raise ValidationError("Coordinates outside of legal bounds")
        return geos.Point(latitude, longitude)


class CreateMarkerForm(forms.Form):
    name = forms.CharField(label="Name", required=True, max_length=100)
    location = CoordinatesField(required=True)


class CreateIssueForm(forms.Form):
    title = forms.CharField(label="Title", required=True, max_length=150)
    latitude = forms.FloatField(label="Latitude", required=True)
    longitude = forms.FloatField(label="Longitude", required=True)
    # location = CoordinatesField(required=True)

    def clean(self):
        if not models.CivicArea.objects.filter(
            area__contains=geos.Point(
                self.cleaned_data["longitude"], self.cleaned_data["latitude"]
            )
        ).exists():
            raise ValidationError("You are out of bounds")
        # return self.cleaned_data['location']
