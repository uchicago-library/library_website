# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0004_auto_20151020_1954'),
        ('units', '0018_unitpage_body'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitpage',
            name='page_maintainer',
            field=models.ForeignKey(to='staff.StaffPage', null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='units_unitpage_related'),
        ),
    ]
