# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime

utc = datetime.timezone.utc


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0031_auto_20151124_0008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(default=datetime.datetime(2015, 11, 24, 17, 56, 23, 317608, tzinfo=utc), blank=True),
        ),
    ]
