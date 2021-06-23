from django.contrib.gis.db import models
from django.contrib.gis.geos import Polygon, MultiPolygon, Point
from django.template.defaultfilters import slugify


class Marker(models.Model):
    name = models.TextField()
    location = models.PointField()

    def __str__(self):
        return self.name


# class StateQuerySet(models.QuerySet):
#     def create_state(self, *, name: str, geometry: MultiPolygon) -> 'State':
#         return self.create(
#             name=name,
#             slug=slugify(name),
#             geometry=geometry)


class CivicPoint(models.Model):
    objects = models.QuerySet().as_manager()

    name = models.TextField()
    # todo so many duplicates
    # slug = models.TextField(db_index=True, unique=True)
    point = models.PointField()

    def __str__(self):
        return self.name

    def __init__(self, name: str, point: Point):
        super().__init__(name=name, point=point)


# todo implemented for state only
class CivicArea(models.Model):
    objects = models.QuerySet().as_manager()

    name = models.TextField()
    slug = models.TextField(db_index=True, unique=True)
    area = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return self.name

    def __init__(self, name: str, area: MultiPolygon):
        super().__init__(name=name, slug=slugify(name), area=area)


class Issue(models.Model):
    objects = models.QuerySet().as_manager()

    created_at = models.DateTimeField(auto_now_add=True)
    title = models.TextField(help_text="Full description of issue")
    location = models.PointField(help_text="Latitude and longitude of issue")

    def __str__(self):
        return self.title

    def url_slug(self):
        return f"-{slugify(self.title)}"
