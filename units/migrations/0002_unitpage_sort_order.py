# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitpage',
            name='sort_order',
            field=models.IntegerField(default=0, blank=True),
        ),
    ]
