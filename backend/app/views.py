import typing

from django.contrib.gis import geos
from django.contrib.gis.measure import Distance
from django.contrib.gis.db.models import Extent, Union
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, reverse
from django.http.request import HttpRequest as StockHttpRequest
from django.views import View
from django.contrib.postgres.search import TrigramDistance
from django.contrib.gis.geos import Point
from pyproj import Geod


from . import forms, models

INDIA_EXTENT = ((8, 68), (37, 97))  # Approximate extent of India


class Request(StockHttpRequest):
    pass
    # user: Union[User, AnonymousUser]


class Home(View):
    def get(self, request):
        return render(request, "app/home.html", {"page_title": "Home"})


class Box:
    box: geos.Polygon
    response: typing.List[typing.Dict]

    def __init__(self, distance: int, lat: float, lon: float):
        # https://stackoverflow.com/questions/46070891/geodjango-how-to-create-a-boundingbox-from-a-central-point-with-10km-x-10km-siz
        g = Geod(ellps="clrk66")
        import math

        distance = math.sqrt(2) * distance
        # given latitude (lat), longitude (lon) values for the location
        top_right_corner = g.fwd(lon, lat, 45, distance)
        bottom_right_corner = g.fwd(lon, lat, 135, distance)
        bottom_left_corner = g.fwd(lon, lat, 225, distance)
        top_left_corner = g.fwd(lon, lat, 315, distance)
        self.box = geos.Polygon.from_bbox(
            (
                bottom_left_corner[0],
                bottom_left_corner[1],
                top_right_corner[0],
                top_right_corner[1],
            )
        )
        self.response = [
            {"lat": top_right_corner[1], "lng": top_right_corner[0]},
            {"lat": top_left_corner[1], "lng": top_left_corner[0]},
            {"lat": bottom_left_corner[1], "lng": bottom_left_corner[0]},
            {"lat": bottom_right_corner[1], "lng": bottom_right_corner[0]},
        ]


class ListIssues(View):
    def get(self, request, latitude: float, longitude: float, distance: int):
        point = Point(longitude, latitude)
        if not models.CivicArea.objects.filter(area__contains=point).exists():
            return HttpResponse("Unsupported area")
        if distance > 50000:
            return HttpResponse("Only upto 50km")
        bounds = Box(distance, latitude, longitude)
        issues = models.Issue.objects.filter(location__contained=bounds.box).order_by(
            "-id"
        )
        issues_response = [
            {
                "id": issue.id,
                "title": issue.title,
                "location": {"lat": issue.location.y, "lng": issue.location.x},
            }
            for issue in issues
        ]
        return render(
            request,
            "app/list_issues.html",
            {
                "page_title": "Issues",  # make some seo friendly title
                "issues": issues_response,
                "bounds": bounds.response,
            },
        )


class CreateIssue(View):
    def get(self, request: Request, latitude: float, longitude: float):
        form = forms.CreateIssueForm(
            initial={"latitude": latitude, "longitude": longitude}
        )
        # tags = [tag.as_response() for tag in Tag.objects.order_by('name')]
        return render(
            request,
            "app/create_issue.html",
            {
                "form": form,
                "page_title": "Report Issue",
                "latitude": latitude,
                "longitude": longitude,
            },
        )

    def post(self, request: Request, latitude: float, longitude: float):
        form = forms.CreateIssueForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                "app/create_issue.html",
                {
                    "form": form,
                    "page_title": "Report Issue",
                    "latitude": latitude,
                    "longitude": longitude,
                },
            )
        with transaction.atomic():
            issue = models.Issue.objects.create(
                title=form.cleaned_data["title"],
                location=geos.Point(
                    form.cleaned_data["longitude"], form.cleaned_data["latitude"]
                ),
            )
        return redirect(reverse("home"))


class SearchPoints(View):
    def get(self, request: Request):
        term = self.request.GET["term"]
        user_location = Point(
            float(self.request.GET["lng"]), float(self.request.GET["lat"])
        )
        p1 = models.CivicPoint.objects.filter(name__icontains=term).filter(
            point__distance_lte=(user_location, Distance(km=30))
        )
        p2 = models.CivicPoint.objects.filter(name__icontains=term).filter(
            point__distance_gt=(user_location, Distance(km=30))
        )
        points = p1.union(p2, all=True)[:20]
        return JsonResponse(
            {
                "points": [
                    {
                        "id": point.id,
                        "name": point.name,
                        "point": {"lat": point.point.y, "lng": point.point.x},
                    }
                    for point in points
                ]
            }
        )
