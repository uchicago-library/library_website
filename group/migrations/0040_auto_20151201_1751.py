# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import group.models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0039_auto_20151201_1701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(blank=True, default=group.models.default_end_time),
        ),
    ]
