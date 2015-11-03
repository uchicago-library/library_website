# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0016_auto_20151021_1917'),
        ('lib_collections', '0029_collectionpage_collection_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collectionpage',
            name='location',
        ),
        migrations.AddField(
            model_name='collectionpage',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, related_name='lib_collections_collectionpage_related', to='units.UnitPage'),
        ),
    ]
