import logging

from django.shortcuts import reverse
from django.contrib.gis import geos
from django.test.utils import ignore_warnings
from django.test import TestCase, Client
from app import forms, models


class MyTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # https://stackoverflow.com/questions/6377231/avoid-warnings-on-404-during-django-test-runs answered Jan 6 2021 at 10:50 by lorey
        # Reduce the log level to avoid errors like 'not found'
        # Has a corresponding code in teardown
        logger = logging.getLogger("django.request")
        self.previous_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)
        # From https://github.com/evansd/whitenoise/issues/215#issuecomment-832276682
        ignore_warnings(message="No directory at", module="whitenoise.base").enable()

    def tearDown(self):
        # Reset the log level back to normal
        logger = logging.getLogger("django.request")
        logger.setLevel(self.previous_level)


class HomeTestCase(MyTestCase):
    def test_home_is_200(self):
        response = self.client.get(reverse("home"))
        self.assertEquals(response.status_code, 200)

    def test_search_points_works(self):
        # todo distance matching too
        c1 = models.CivicPoint.create("foo", geos.Point(60, 60))
        c2 = models.CivicPoint.create("food", geos.Point(60.01, 60.01))
        c3 = models.CivicPoint.create("bar", geos.Point(60.02, 60.02))
        response = self.client.get(
            reverse("search_points"), {"term": "foo", "lat": 60, "lng": 60}
        )
        points = response.json()["points"]
        self.assertEquals(len(points), 2)
        self.assertEquals(points[0]["id"], c1.id)
        self.assertEquals(points[1]["id"], c2.id)


class IssueTestCase(MyTestCase):
    def test_view_issue_is_fine(self):
        issue = models.Issue.objects.create(
            title="title",
            location=geos.Point(60, 60),
        )
        response = self.client.get(reverse("view_issue", args=(0,)))
        self.assertEquals(response.status_code, 404)
        response = self.client.get(reverse("view_issue", args=(issue.id,)))
        self.assertEquals(response.status_code, 200)
        # self.assertInHTML('title', response.content.decode())
        self.assertContains(response, "title")


class CreateIssueTestCase(MyTestCase):
    def test_form(self):
        tag_1 = models.Tag.create("Tag 1")
        form = forms.CreateIssueForm(
            {"title": "foo", "latitude": 60, "longitude": 60, "tags": "tag-1"}
        )
        self.assertTrue(form.is_valid())
        form = forms.CreateIssueForm(
            {"title": "foo", "latitude": 60, "longitude": 60, "tags": "tag-fake"}
        )
        self.assertEquals(list(form.errors.keys()), ["tags"])
        form = forms.CreateIssueForm(
            {"title": "foo", "latitude": 600, "longitude": 60, "tags": "tag-1"}
        )
        self.assertEquals(list(form.errors.keys()), ["latitude"])
        form = forms.CreateIssueForm(
            {"title": "foo", "latitude": 60, "longitude": 600, "tags": "tag-1"}
        )
        self.assertEquals(list(form.errors.keys()), ["longitude"])

    def test_raw_data_contains_latitude_and_longitude(self):
        response = self.client.get(reverse("create_issue", args=(60.25, 61.75)))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "60.25")
        self.assertContains(response, "61.75")

    def test_creating_issue_works(self):
        tag_1 = models.Tag.create("Tag 1")
        tag_2 = models.Tag.create("Tag 2")
        response = self.client.post(
            reverse("create_issue", args=(60, 60)), {"latitude": 0, "longitude": 0}
        )
        self.assertEquals(response.status_code, 400)
        self.assertFalse(response.context_data["form"].is_valid())
        response = self.client.post(
            reverse("create_issue", args=(60, 60)),
            {"title": "foo", "latitude": 60, "longitude": 60, "tags": "tag-1,tag-2"},
        )
        # self.assertEquals(response.status_code, 301)
        issue = models.Issue.objects.get()
        self.assertEquals(issue.title, "foo")
        self.assertEquals(list(issue.tags.all()), [tag_1, tag_2])
        self.assertEquals(list(issue.tag_slugs), ["tag-1", "tag-2"])
        self.assertEquals(issue.location.tuple, geos.Point(60, 60).tuple)
        self.assertRedirects(
            response, reverse("view_issue", args=(issue.id,)), status_code=301
        )


class ListIsuesTestCase(MyTestCase):
    def test_distance_limit_is_checked(self):
        response = self.client.get(reverse("list_issues", args=(60, 60, 100000)))
        self.assertEquals(response.status_code, 200)
        response = self.client.get(reverse("list_issues", args=(60, 60, 200000)))
        self.assertEquals(response.status_code, 400)

    # todo checking if issues are within bounds

    def test_tag_filters(self):
        tag_1 = models.Tag.create("Foo 1")
        tag_2 = models.Tag.create("Foo 2")
        tag_3 = models.Tag.create("Foo 3")
        tag_4 = models.Tag.create("Foo 4")
        issue_1 = models.Issue.create(
            title="Issue 1", location=geos.Point(60, 60), tags=[tag_1, tag_2]
        )
        issue_2 = models.Issue.create(
            title="Issue 2", location=geos.Point(60, 60), tags=[tag_1]
        )
        issue_3 = models.Issue.create(
            title="Issue 3", location=geos.Point(60, 60), tags=[tag_3]
        )

        def issue_ids_in_context(response):
            return [
                issue["id"] for issue in response.context_data["raw_data"]["rawIssues"]
            ]

        response = self.client.get(
            reverse("list_issues", args=(60, 60, 100000)),
            {"all_tags": f"{tag_1.slug},{tag_2.slug}"},
        )
        self.assertEquals(issue_ids_in_context(response), [issue_1.id])
        response = self.client.get(
            reverse("list_issues", args=(60, 60, 100000)),
            {"any_tags": f"{tag_1.slug},{tag_2.slug}"},
        )
        self.assertEquals(issue_ids_in_context(response), [issue_2.id, issue_1.id])
        response = self.client.get(
            reverse("list_issues", args=(60, 60, 100000)),
            {"none_tags": f"{tag_1.slug},{tag_2.slug}"},
        )
        self.assertEquals(issue_ids_in_context(response), [issue_3.id])
