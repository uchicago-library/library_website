# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0016_auto_20151120_1957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(default=datetime.datetime(2015, 11, 20, 20, 58, 14, 728746, tzinfo=utc), blank=True),
        ),
    ]
