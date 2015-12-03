# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0017_auto_20151202_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitindexpage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='units_unitindexpage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='unitindexpage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='units_unitindexpage_maintainer', null=True),
        ),
        migrations.AlterField(
            model_name='unitpage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='units_unitpage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='unitpage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='units_unitpage_maintainer', null=True),
        ),
    ]
