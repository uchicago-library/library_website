# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='intranetsidebarpage',
            name='editor',
            field=models.ForeignKey(related_name='base_intranetsidebarpage_editor', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='intranetsidebarpage',
            name='page_maintainer',
            field=models.ForeignKey(related_name='base_intranetsidebarpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='intranetplainpage',
            name='editor',
            field=models.ForeignKey(related_name='base_intranetplainpage_editor', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='intranetplainpage',
            name='page_maintainer',
            field=models.ForeignKey(related_name='base_intranetplainpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
    ]
