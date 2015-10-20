# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0001_initial'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouppage',
            name='chair',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='groupmember',
            name='group',
            field=models.ForeignKey(to='group.GroupPage'),
        ),
        migrations.AddField(
            model_name='groupmember',
            name='staff',
            field=models.ForeignKey(to='staff.StaffPage'),
        ),
    ]
