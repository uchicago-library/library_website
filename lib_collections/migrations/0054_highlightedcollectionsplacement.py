# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0053_auto_20151026_2006'),
    ]

    operations = [
        migrations.CreateModel(
            name='HighlightedCollectionsPlacement',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('collection', models.ForeignKey(to='lib_collections.CollectionPage', on_delete=django.db.models.deletion.SET_NULL, related_name='highlighted_collections', null=True)),
                ('parent', modelcluster.fields.ParentalKey(to='lib_collections.CollectingAreaPage', on_delete=django.db.models.deletion.SET_NULL, related_name='highlighted_collection_placements', null=True)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
