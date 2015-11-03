# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0005_remove_grouppage_meeting_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouppage',
            name='meeting_time',
            field=models.TimeField(blank=True, default=datetime.datetime(2015, 10, 31, 3, 30, 34, 673941)),
        ),
    ]
