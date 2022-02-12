from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.CivicPoint)
admin.site.register(models.CivicArea)
admin.site.register(models.Issue)
