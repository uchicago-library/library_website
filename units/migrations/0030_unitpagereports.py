# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0029_remove_unitpage_body_two'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnitPageReports',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('date', models.DateField()),
                ('summary', models.TextField()),
                ('link', models.URLField(default='', max_length=254)),
                ('page', modelcluster.fields.ParentalKey(related_name='unit_reports', to='units.UnitPage')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
    ]
