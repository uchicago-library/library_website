# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0050_collectingareapage_subject'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectingAreaPageStacksRanges',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('stacks_range', models.CharField(max_length=100, blank=True)),
                ('stacks_URL', models.URLField(max_length=254, blank=True, default='')),
                ('page', modelcluster.fields.ParentalKey(related_name='stacks_ranges', to='lib_collections.CollectingAreaPage')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
    ]
