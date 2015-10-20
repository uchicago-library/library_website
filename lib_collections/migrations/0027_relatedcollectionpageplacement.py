# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0026_collectionpage_thumbnail'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelatedCollectionPagePlacement',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('sort_order', models.IntegerField(null=True, blank=True, editable=False)),
                ('parent', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, related_name='related_page_placement', to='lib_collections.CollectionPage')),
                ('related_page', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, related_name='related_page', to='lib_collections.CollectionPage')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
    ]
