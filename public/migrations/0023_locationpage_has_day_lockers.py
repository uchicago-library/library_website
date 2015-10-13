# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0022_auto_20151001_1637'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationpage',
            name='has_day_lockers',
            field=models.BooleanField(default=False),
        ),
    ]
