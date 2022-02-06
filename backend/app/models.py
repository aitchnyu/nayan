import typing

# from django.db.models import QuerySet
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q, Func, Count, F, Value, ExpressionWrapper
from django.contrib.gis.db import models
from django.contrib.gis.geos import Polygon, MultiPolygon, Point
from django.template.defaultfilters import slugify


class Marker(models.Model):
    name = models.TextField()
    location = models.PointField()

    def __str__(self):
        return self.name


class CivicPoint(models.Model):
    objects = models.QuerySet().as_manager()

    name = models.TextField()
    # todo so many duplicates
    # slug = models.TextField(db_index=True, unique=True)
    point = models.PointField()

    def __str__(self):
        return self.name

    @classmethod
    def create(cls, name: str, point: Point):
        return cls(name=name, point=point)


# todo implemented for state only
class CivicArea(models.Model):
    objects = models.QuerySet().as_manager()

    name = models.TextField()
    slug = models.TextField(db_index=True, unique=True)
    area = models.MultiPolygonField(srid=4326)

    def __str__(self):
        return self.name


class TagQuerySet(models.QuerySet):
    def create_tag(self, name: str) -> "Tag":
        return self.create(name=name, slug=slugify(name))


class Tag(models.Model):
    objects: TagQuerySet = TagQuerySet.as_manager()

    name = models.TextField()
    slug = models.TextField()

    def __str__(self):
        return f"{self.id} {self.name}"

    def as_response(self) -> dict:
        return {"slug": self.slug, "name": self.name}


# todo no user, state, district etc
class IssueQuerySet(models.QuerySet):
    def create_issue(
        self,
        *,
        title: str,
        location: Point,
        tags: typing.Sequence[Tag],
    ) -> "Issue":
        new_issue = self.create(
            title=title, location=location, tag_slugs=[tag.slug for tag in tags]
        )
        new_issue.tags.add(*tags)
        return new_issue

    def filter_tags(
        self,
        *,
        all_tags: typing.List[Tag],
        any_tags: typing.List[Tag],
        none_tags: typing.List[Tag],
    ) -> typing.Union[models.QuerySet, typing.List["Issue"]]:
        query = self
        if all_tags:
            query = query.filter(tag_slugs__contains=[i.slug for i in all_tags])
        if any_tags:
            query = query.filter(tag_slugs__overlap=[i.slug for i in any_tags])
        if none_tags:
            query = query.exclude(tag_slugs__overlap=[i.slug for i in none_tags])
        return query

    def tag_counts(self) -> typing.Sequence[dict]:
        return (
            Tag.objects.filter(issue__id__in=self)
            .annotate(count=Count("slug"))
            .order_by("-count")
            .values("slug", "name", "count")
        )


class Issue(models.Model):
    objects = IssueQuerySet.as_manager()

    created_at = models.DateTimeField(auto_now_add=True)
    title = models.TextField(help_text="Full description of issue")
    location = models.PointField(help_text="Latitude and longitude of issue")

    tag_slugs = ArrayField(models.CharField(max_length=30), db_index=True, default=list)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title

    def url_slug(self):
        return f"-{slugify(self.title)}"
