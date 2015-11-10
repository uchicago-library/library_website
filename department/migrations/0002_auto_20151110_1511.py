# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),
        ('department', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='departmentpage',
            name='editor',
            field=models.ForeignKey(related_name='department_departmentpage_editor', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='departmentpage',
            name='page_maintainer',
            field=models.ForeignKey(related_name='department_departmentpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
    ]
