# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_auto_20151201_2209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intranetplainpage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='base_intranetplainpage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='intranetplainpage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='base_intranetplainpage_maintainer', null=True),
        ),
    ]
