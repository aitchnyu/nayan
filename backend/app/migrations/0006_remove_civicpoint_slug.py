# Generated by Django 3.2 on 2021-05-18 10:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0005_auto_20210518_0936"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="civicpoint",
            name="slug",
        ),
    ]