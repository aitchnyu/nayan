from django import forms
from django.contrib.gis import geos
from django.forms import ValidationError

from . import models


class TagSlugsField(forms.Field):
    min_tags: int
    max_tags: int

    def __init__(self, *, min_tags=0, max_tags=4, **kwargs):
        self.min_tags = min_tags
        self.max_tags = max_tags
        super().__init__(**kwargs)

    def clean(self, value: str):
        if value is None:
            slugs = []
        else:
            slugs = [i for i in value.split(",") if i != ""]
        if len(slugs) < self.min_tags or len(slugs) > self.max_tags:
            raise ValidationError(
                f"There must be between {self.min_tags} and {self.max_tags} tags",
                code="invalid_tag_counts",
            )
        existing_tags = models.Tag.objects.filter(slug__in=slugs)
        missing_slugs = set(slugs) - set([tag.slug for tag in existing_tags])
        if missing_slugs:
            raise ValidationError(
                "Invalid tags: " + ",".join(missing_slugs), code="invalid_tags"
            )
        return list(existing_tags)


class CreateIssueForm(forms.Form):
    title = forms.CharField(label="Title", required=True, max_length=150)
    latitude = forms.FloatField(label="Latitude", required=True)
    longitude = forms.FloatField(label="Longitude", required=True)
    tags = TagSlugsField(min_tags=1, max_tags=4)

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


class ListIssuesParamsForm(forms.Form):
    state_slug: str
    # todo implement this next
    # date_range = DateRangeField(required=False)
    distance = forms.IntegerField(label="Distance", max_value=100000)
    any_tags = TagSlugsField(max_tags=10)
    all_tags = TagSlugsField(max_tags=10)
    none_tags = TagSlugsField(max_tags=10)
    # todo sane values for this
    # big_pages = TrueFalseField(required=False)
    # page = forms.IntegerField(required=False, min_value=1, max_value=500)

    # def clean(self):
    # todo check tags list so they dont overlap
