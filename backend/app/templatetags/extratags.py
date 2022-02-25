import json

from django import template
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import QueryDict
from django.http.request import HttpRequest
from django.utils.http import urlencode
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def base_url(request: HttpRequest):
    return request._current_scheme_host


@register.filter
def encodejson(value):
    return json.dumps(value, cls=DjangoJSONEncoder)


# todo For later use

# @register.simple_tag
# def hcaptcha_sitekey():
#     return settings.HCAPTCHA_SITEKEY
#
# @register.filter
# def none_for_1(value):
#     return None if value == 1 else value
#
#
# @register.simple_tag
# def url_with_args(value: QueryDict, **kwargs):
#     shit = {k: v for k, v in {**value.dict(), **kwargs}.items() if v}
#     return "?" + urlencode(shit)
