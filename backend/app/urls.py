from django.urls import path, register_converter

from . import views

# Copy pasted from https://www.webforefront.com/django/accessurlparamstemplates.html
# Pattern from https://stackoverflow.com/a/4703409/604511
class FloatConverter:
    regex = "[-+]?\d*\.\d+|\d+"

    def to_python(self, value):
        return float(value)

    def to_url(self, value):
        return "{}".format(value)


register_converter(FloatConverter, "float")

urlpatterns = [
    path("", views.Home.as_view(), name="home"),
    path(
        "issues/<float:latitude>/<float:longitude>/<int:distance>",
        views.ListIssues.as_view(),
        name="list_issues",
    ),
    path(
        "issues/<float:latitude>/<float:longitude>/create",
        views.CreateIssue.as_view(),
        name="create_issue",
    ),
    path("api/points/search", views.SearchPoints.as_view(), name="search_points"),
]
