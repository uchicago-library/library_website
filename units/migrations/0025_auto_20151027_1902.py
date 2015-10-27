# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0009_remove_staffpage_is_subject_specialist'),
        ('units', '0024_auto_20151022_1854'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitpage',
            name='content_specialist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='units_unitpage_content_specialist'),
        ),
        migrations.AddField(
            model_name='unitpage',
            name='editor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='units_unitpage_editor'),
        ),
        migrations.AlterField(
            model_name='unitpage',
            name='page_maintainer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='units_unitpage_maintainer'),
        ),
    ]
