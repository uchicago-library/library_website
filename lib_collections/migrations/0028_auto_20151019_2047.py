# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0027_relatedcollectionpageplacement'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='relatedcollectionpageplacement',
            name='related_page',
        ),
        migrations.AddField(
            model_name='relatedcollectionpageplacement',
            name='related_collection',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, to='lib_collections.CollectionPage', related_name='related_collection'),
        ),
        migrations.AlterField(
            model_name='relatedcollectionpageplacement',
            name='parent',
            field=modelcluster.fields.ParentalKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, to='lib_collections.CollectionPage', related_name='related_collection_placement'),
        ),
    ]
