# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime

utc = datetime.timezone.utc


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0035_auto_20151125_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(default=datetime.datetime(2015, 11, 25, 18, 33, 17, 721196, tzinfo=utc), blank=True),
        ),
    ]
