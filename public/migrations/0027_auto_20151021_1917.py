# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0016_auto_20151021_1917'),
        ('public', '0026_auto_20151020_1954'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donorpage',
            name='location',
        ),
        migrations.RemoveField(
            model_name='locationpage',
            name='location',
        ),
        migrations.RemoveField(
            model_name='standardpage',
            name='location',
        ),
        migrations.AddField(
            model_name='donorpage',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, related_name='public_donorpage_related', to='units.UnitPage'),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, related_name='public_locationpage_related', to='units.UnitPage'),
        ),
        migrations.AddField(
            model_name='standardpage',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, related_name='public_standardpage_related', to='units.UnitPage'),
        ),
    ]
