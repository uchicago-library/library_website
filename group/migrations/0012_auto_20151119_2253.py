# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0011_grouppage_meeting_end_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='grouppage',
            old_name='meeting_time',
            new_name='meeting_start_time',
        ),
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(blank=True, default=datetime.datetime(2015, 11, 19, 23, 53, 18, 310536, tzinfo=utc)),
        ),
    ]
