# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0027_auto_20151123_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(blank=True, default=datetime.datetime(2015, 11, 23, 19, 27, 14, 860147, tzinfo=utc)),
        ),
    ]
