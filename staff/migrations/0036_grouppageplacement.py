# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staffweb', '0001_initial'),
        ('staff', '0035_auto_20151029_2133'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupPagePlacement',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('sort_order', models.IntegerField(blank=True, null=True, editable=False)),
                ('group_or_committee', models.ForeignKey(related_name='group_page', to='staffweb.GroupCommitteePage', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True)),
                ('parent', modelcluster.fields.ParentalKey(null=True, to='staff.StaffPage', related_name='group_page_placements', on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
