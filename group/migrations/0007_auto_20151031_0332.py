# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0006_grouppage_meeting_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_time',
            field=models.TimeField(default=django.utils.timezone.now, blank=True),
        ),
    ]
