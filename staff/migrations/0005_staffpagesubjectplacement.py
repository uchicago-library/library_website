# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0002_auto_20151022_1913'),
        ('staff', '0004_auto_20151020_1954'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffPageSubjectPlacement',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, blank=True, editable=False)),
                ('page', modelcluster.fields.ParentalKey(to='staff.StaffPage', related_name='staff_subject_placements')),
                ('subject', models.ForeignKey(to='subjects.Subject', related_name='+')),
            ],
            options={
                'verbose_name_plural': 'Subject Placements',
                'verbose_name': 'Subject Placement',
            },
        ),
    ]
