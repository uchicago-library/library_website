# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0004_auto_20151020_1954'),
        ('lib_collections', '0030_auto_20151021_1917'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionpage',
            name='staff_contact',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='staff.StaffPage'),
        ),
    ]
