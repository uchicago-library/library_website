# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0014_remove_locationpage_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationpage',
            name='parent_building',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='public.LocationPage'),
        ),
        migrations.AlterField(
            model_name='locationpage',
            name='location',
            field=models.ForeignKey(blank=True, null=True, related_name='public_locationpage_related', on_delete=django.db.models.deletion.SET_NULL, to='public.LocationPage'),
        ),
        migrations.AlterField(
            model_name='standardpage',
            name='location',
            field=models.ForeignKey(blank=True, null=True, related_name='public_standardpage_related', on_delete=django.db.models.deletion.SET_NULL, to='public.LocationPage'),
        ),
    ]
