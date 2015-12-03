# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0042_auto_20151202_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupindexpage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='group_groupindexpage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='groupindexpage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='group_groupindexpage_maintainer', null=True),
        ),
        migrations.AlterField(
            model_name='grouppage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='group_grouppage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='grouppage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='group_grouppage_maintainer', null=True),
        ),
    ]
