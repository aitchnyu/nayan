# Generated by Django 3.2 on 2021-06-28 18:04

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0008_auto_20210628_1803"),
    ]

    operations = [
        migrations.AlterField(
            model_name="issue",
            name="tag_slugs",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=30),
                db_index=True,
                default=list,
                size=None,
            ),
        ),
    ]
