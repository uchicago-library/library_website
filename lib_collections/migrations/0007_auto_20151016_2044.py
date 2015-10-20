# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0006_collectionpage_format'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionPageFormatPlacement',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('advert', models.ForeignKey(to='lib_collections.Format', related_name='+')),
            ],
            options={
                'verbose_name': 'Collection Placement',
                'verbose_name_plural': 'Collection Placements',
            },
        ),
        migrations.RemoveField(
            model_name='collectionpage',
            name='format',
        ),
        migrations.AddField(
            model_name='collectionpageformatplacement',
            name='page',
            field=modelcluster.fields.ParentalKey(to='lib_collections.CollectionPage', related_name='collection_placements'),
        ),
    ]
