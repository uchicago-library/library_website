# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0037_auto_20151031_0320'),
        ('group', '0011_grouppagereports'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupMembers',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('sort_order', models.IntegerField(null=True, blank=True, editable=False)),
                ('parent', modelcluster.fields.ParentalKey(null=True, related_name='group_members', to='group.GroupPage', on_delete=django.db.models.deletion.SET_NULL)),
                ('staff_members', models.ForeignKey(null=True, blank=True, related_name='member', to='staff.StaffPage', on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
    ]
