# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import group.models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0056_auto_20151228_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(blank=True, default=group.models.default_end_time, null=True),
        ),
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_start_time',
            field=models.TimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]
