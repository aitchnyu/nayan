import os
import time
import typing

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.shortcuts import reverse
from django.contrib.gis import geos
from playwright.sync_api import sync_playwright, Browser
from app import forms, models

from django.urls import resolve
from urllib.parse import urlparse, parse_qsl, urlsplit


class PathMatch:
    view_name: str
    args: dict
    query: dict

    def __init__(self, stuff):
        parsed = urlparse(stuff)
        match = resolve(parsed.path)
        self.view_name = match.url_name
        self.args = match.kwargs
        self.query = dict(parse_qsl(urlsplit(stuff).query))

    def __str__(self):
        return f"<PathMatch view={self.view_name} args={self.args} query={self.query}>"


class HomepageLiveServerTestCase(StaticLiveServerTestCase):
    playwright: typing.Any
    browser: Browser

    # Copied from https://github.com/mxschmitt/python-django-playwright/blob/master/test_login.py

    # todo dry this, copy stuff from other
    @classmethod
    def setUpClass(cls):
        # We will get following error if this is not enabled
        # django.core.exceptions.SynchronousOnlyOperation: You cannot call this from an async context - use a thread or sync_to_async.
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.firefox.launch()
        cls.browser_context = cls.browser.new_context(
            geolocation={"latitude": 60.60, "longitude": 65},
            permissions=["geolocation"],
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.close()
        cls.playwright.stop()

    def test_url_for_geolocation_and_url_for_location_changes_after_dragging_amp(self):
        page = self.browser_context.new_page()
        page.set_default_timeout(5000)
        page.goto(f"{self.live_server_url}/")
        page.wait_for_selector(".issues-at-geolocation")
        self.assertIn(
            "/issues/60.6/65/1000",
            page.eval_on_selector(".issues-at-geolocation", "el => el.href"),
        )
        self.assertIn(
            "/issues/60.6/65/1000",
            page.eval_on_selector(".issues-at-map-center", "el => el.href"),
        )
        bounding_box = page.locator("div.leaflet-container").bounding_box()
        page.mouse.move(
            bounding_box["x"] + bounding_box["width"] / 2,
            bounding_box["y"] + bounding_box["height"] / 2,
            steps=5,
        )
        page.mouse.down()
        page.mouse.move(bounding_box["x"] + 100, bounding_box["y"] + 100, steps=5)
        page.mouse.up()
        match = PathMatch(
            page.eval_on_selector(".issues-at-map-center", "el => el.href")
        )
        self.assertAlmostEqual(match.args["latitude"], 60.6, delta=0.01)
        self.assertAlmostEqual(match.args["longitude"], 65, delta=0.01)
        page.close()

    def test_url_for_user_selected_location_is_shown(self):
        page = self.browser_context.new_page()
        c1 = models.CivicPoint.create("foo", geos.Point(60.88, 60.88))
        page.set_default_timeout(5000)
        page.goto(f"{self.live_server_url}/")
        page.focus("input[type=text]")
        page.type("input[type=text]", "foo")
        page.locator("a.dropdown-item").click()
        self.assertIn(
            "/issues/60.88/60.88/1000",
            page.eval_on_selector(".issues-at-named-location", "el => el.href"),
        )
        page.close()


class ListIssuesLiveServerTestCase(StaticLiveServerTestCase):
    playwright: typing.Any
    browser: Browser

    # Copied from https://github.com/mxschmitt/python-django-playwright/blob/master/test_login.py

    @classmethod
    def setUpClass(cls):
        # We will get following error if this is not enabled
        # django.core.exceptions.SynchronousOnlyOperation: You cannot call this from an async context - use a thread or sync_to_async.
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.firefox.launch()
        cls.browser_context = cls.browser.new_context()
        # cls.browser.set_default_timeout(1000)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.close()
        cls.playwright.stop()

    def test_recenter_url_is_updated_on_zoom_and_maximum_value_of_100000_meters(self):
        page = self.browser_context.new_page()
        # c1 = models.CivicPoint.create("foo", geos.Point(60.88, 60.88))
        page.set_default_timeout(5000)
        page.goto(
            self.live_server_url + reverse("list_issues", args=(60.6, 60.6, 1000))
        )
        match = PathMatch(page.eval_on_selector(".recenter-map-url", "el => el.href"))
        self.assertAlmostEqual(match.args["latitude"], 60.6, delta=0.01)
        self.assertAlmostEqual(match.args["longitude"], 60.6, delta=0.01)
        self.assertAlmostEqual(match.args["distance"], 1000, delta=10)

        page.locator(".leaflet-control-zoom-out").click()
        time.sleep(0.2)
        match = PathMatch(page.eval_on_selector(".recenter-map-url", "el => el.href"))
        self.assertAlmostEqual(match.args["latitude"], 60.6, delta=0.01)
        self.assertAlmostEqual(match.args["longitude"], 60.6, delta=0.01)
        self.assertNotAlmostEqual(match.args["distance"], 1000, delta=10)

        page.locator(".leaflet-control-zoom-out").click(delay=250, click_count=8)
        match = PathMatch(page.eval_on_selector(".recenter-map-url", "el => el.href"))
        self.assertAlmostEqual(match.args["latitude"], 60.6, delta=0.01)
        self.assertAlmostEqual(match.args["longitude"], 60.6, delta=0.01)
        self.assertEqual(match.args["distance"], 100000)

        page.close()
