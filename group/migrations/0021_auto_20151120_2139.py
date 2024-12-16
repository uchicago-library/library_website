# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime

utc = datetime.timezone.utc


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0020_auto_20151120_2139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(default=datetime.datetime(2015, 11, 20, 22, 39, 35, 823118, tzinfo=utc), blank=True),
        ),
    ]
