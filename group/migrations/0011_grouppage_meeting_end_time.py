# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime

utc = datetime.timezone.utc


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0010_auto_20151119_2133'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(default=datetime.datetime(2015, 11, 19, 23, 50, 45, 710810, tzinfo=utc), blank=True),
        ),
    ]
