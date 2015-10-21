# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0015_unitpage_public_web_page'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unitpage',
            name='location',
        ),
        migrations.AddField(
            model_name='unitpage',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, related_name='units_unitpage_related', to='units.UnitPage'),
        ),
    ]
