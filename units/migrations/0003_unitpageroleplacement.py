# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0002_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnitPageRolePlacement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(editable=False, null=True, blank=True)),
                ('page', modelcluster.fields.ParentalKey(to='units.UnitPage', related_name='unit_placements')),
                ('role', models.ForeignKey(to='units.Role', related_name='+')),
            ],
            options={
                'verbose_name': 'Unit Placement',
                'verbose_name_plural': 'Unit Placements',
            },
        ),
    ]
