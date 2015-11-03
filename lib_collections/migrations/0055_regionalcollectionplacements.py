# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0054_highlightedcollectionsplacement'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegionalCollectionPlacements',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('name', models.CharField(max_length=254, blank=True)),
                ('description', models.TextField(blank=True)),
                ('page', modelcluster.fields.ParentalKey(to='lib_collections.CollectingAreaPage', related_name='regional_collections')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
