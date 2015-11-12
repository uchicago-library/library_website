# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_auto_20151112_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='newspage',
            name='publish_on',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
