# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0025_donorpage'),
        ('lib_collections', '0028_auto_20151019_2047'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionpage',
            name='collection_location',
            field=models.ForeignKey(to='public.LocationPage', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
    ]
