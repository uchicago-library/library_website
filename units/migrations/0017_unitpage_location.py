# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0027_auto_20151021_1917'),
        ('units', '0016_auto_20151021_1917'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitpage',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, related_name='units_unitpage_related', to='public.LocationPage'),
        ),
    ]
