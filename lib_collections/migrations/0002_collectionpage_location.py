# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0001_initial'),
        ('lib_collections', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionpage',
            name='location',
            field=models.ForeignKey(related_name='lib_collections_collectionpage_related', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='public.LocationPage', null=True),
        ),
    ]
