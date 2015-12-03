# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0004_auto_20151202_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffindexpage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='staff_staffindexpage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='staffindexpage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='staff_staffindexpage_maintainer', null=True),
        ),
        migrations.AlterField(
            model_name='staffpage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='staff_staffpage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='staffpage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='staff_staffpage_maintainer', null=True),
        ),
    ]
