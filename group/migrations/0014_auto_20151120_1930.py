# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime

utc = datetime.timezone.utc


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0013_auto_20151120_1921'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grouppage',
            name='intro',
        ),
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(default=datetime.datetime(2015, 11, 20, 20, 30, 41, 452466, tzinfo=utc), blank=True),
        ),
    ]
