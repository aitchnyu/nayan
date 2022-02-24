import typing

# from django.db.models import QuerySet
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q, Func, Count, F, Value, ExpressionWrapper
from django.contrib.gis.db import models
from django.contrib.gis.geos import Polygon, MultiPolygon, Point
from django.template.defaultfilters import slugify


class CivicPoint(models.Model):
    objects = models.QuerySet().as_manager()

    name = models.TextField()
    # todo so many duplicates in our data
    # slug = models.TextField(db_index=True, unique=True)
    point = models.PointField()

    def __str__(self):  # pragma: no cover
        return self.name

    @classmethod
    def create(cls, name: str, point: Point):
        return cls.objects.create(name=name, point=point)


# todo implemented for state only
class CivicArea(models.Model):
    objects = models.QuerySet().as_manager()

    name = models.TextField()
    slug = models.TextField(db_index=True, unique=True)
    area = models.MultiPolygonField(srid=4326)

    def __str__(self):  # pragma: no cover
        return self.name


class TagQuerySet(models.QuerySet):
    pass

    # todo use tags in future
    # def create_tag(self, name: str) -> "Tag":
    #     return self.create(name=name, slug=slugify(name))


class Tag(models.Model):
    objects: TagQuerySet = TagQuerySet.as_manager()

    name = models.TextField()
    slug = models.TextField()

    def __str__(self):  # pragma: no cover
        return f"{self.id} {self.name}"

    @classmethod
    def create(cls, name) -> "Tag":
        return cls.objects.create(name=name, slug=slugify(name))

    def as_response(self) -> dict:
        return {"slug": self.slug, "name": self.name}


class IssueQuerySet(models.QuerySet):
    def filter_all_tags(
        self, tags: typing.List[Tag]
    ) -> typing.Union[models.QuerySet, typing.List["Issue"]]:
        if tags:
            return self.filter(tag_slugs__contains=[i.slug for i in tags])
        else:
            return self

    def filter_any_tags(
        self, tags: typing.List[Tag]
    ) -> typing.Union[models.QuerySet, typing.List["Issue"]]:
        if tags:
            return self.filter(tag_slugs__overlap=[i.slug for i in tags])
        else:
            return self

    def exclude_tags(
        self, tags: typing.List[Tag]
    ) -> typing.Union[models.QuerySet, typing.List["Issue"]]:
        if tags:
            return self.exclude(tag_slugs__overlap=[i.slug for i in tags])
        else:
            return self

    # def tag_counts(self) -> typing.Sequence[dict]:
    #     return (
    #         Tag.objects.filter(issue__id__in=self)
    #         .annotate(count=Count("slug"))
    #         .order_by("-count")
    #         .values("slug", "name", "count")
    #     )


class Issue(models.Model):
    objects = IssueQuerySet.as_manager()

    created_at = models.DateTimeField(auto_now_add=True)
    title = models.TextField(help_text="Full description of issue")
    location = models.PointField(help_text="Latitude and longitude of issue")

    tag_slugs = ArrayField(models.CharField(max_length=30), db_index=True, default=list)
    tags = models.ManyToManyField(Tag)

    def __str__(self):  # pragma: no cover
        return self.title

    @classmethod
    def create(
        cls,
        *,
        title: str,
        location: Point,
        tags: typing.Sequence[Tag],
    ) -> "Issue":
        new_issue = cls.objects.create(
            title=title, location=location, tag_slugs=[tag.slug for tag in tags]
        )
        new_issue.tags.add(*tags)
        return new_issue
