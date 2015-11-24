# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0015_auto_20151120_1931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(default=datetime.datetime(2015, 11, 20, 20, 56, 59, 256124, tzinfo=utc), blank=True),
        ),
    ]
