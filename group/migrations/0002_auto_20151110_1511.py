# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0001_initial'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupmembers',
            name='group_member',
            field=models.ForeignKey(related_name='member', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='groupmembers',
            name='parent',
            field=modelcluster.fields.ParentalKey(related_name='group_members', on_delete=django.db.models.deletion.SET_NULL, to='group.GroupPage', null=True),
        ),
    ]
