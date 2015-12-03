# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20151202_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectindexpage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='projects_projectindexpage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='projectindexpage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='projects_projectindexpage_maintainer', null=True),
        ),
        migrations.AlterField(
            model_name='projectpage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='projects_projectpage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='projectpage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='projects_projectpage_maintainer', null=True),
        ),
    ]
