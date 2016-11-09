# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0000_manual_pre_initial'),
        ('group', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouppage',
            name='editor',
            field=models.ForeignKey(to='staff.StaffPage', related_name='group_grouppage_editor', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='grouppage',
            name='page_maintainer',
            field=models.ForeignKey(to='staff.StaffPage', related_name='group_grouppage_maintainer', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='groupmembers',
            name='group_member',
            field=models.ForeignKey(to='staff.StaffPage', on_delete=django.db.models.deletion.SET_NULL, related_name='member', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='groupmembers',
            name='parent',
            field=modelcluster.fields.ParentalKey(to='group.GroupPage', related_name='group_members', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
    ]
