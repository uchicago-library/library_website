# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20151104_2039'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newspage',
            name='feature_image',
        ),
        migrations.AddField(
            model_name='newspage',
            name='sticky_until',
            field=models.DateField(default=datetime.date(2015, 11, 4)),
        ),
    ]
