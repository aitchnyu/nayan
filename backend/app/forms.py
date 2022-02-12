from django import forms
from django.contrib.gis import geos
from django.forms import ValidationError

from . import models

# todo For later use
# class CoordinatesField(forms.Field):
#     def clean(self, value: str):
#         try:
#             raw_latitude, raw_longitude = value.split(",")
#             latitude = float(raw_latitude)
#             longitude = float(raw_longitude)
#         except ValueError:  # Cant split, cant parse
#             raise ValidationError("Malformed Location")
#         if latitude < 0 or latitude > 90 or longitude < -180 or longitude > 180:
#             raise ValidationError("Coordinates outside of legal bounds")
#         return geos.Point(latitude, longitude)


class CreateIssueForm(forms.Form):
    title = forms.CharField(label="Title", required=True, max_length=150)
    latitude = forms.FloatField(label="Latitude", required=True)
    longitude = forms.FloatField(label="Longitude", required=True)

    def clean_latitude(self):
        latitude = self.cleaned_data["latitude"]
        if not (-90 <= latitude <= 90):
            raise ValidationError("invalid latitude")
        return latitude

    def clean_longitude(self):
        longitude = self.cleaned_data["longitude"]
        if not (-180 <= longitude <= 180):
            raise ValidationError("invalid longitude")
        return longitude
