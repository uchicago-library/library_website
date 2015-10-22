# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0022_auto_20151022_1817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitpage',
            name='page_maintainer',
            field=models.ForeignKey(related_name='units_unitpage_related_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, blank=True),
        ),
    ]
