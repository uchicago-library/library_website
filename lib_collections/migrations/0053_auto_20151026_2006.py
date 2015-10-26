# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0052_collectingareareferencelocationplacement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectingareareferencelocationplacement',
            name='parent',
            field=modelcluster.fields.ParentalKey(null=True, related_name='reference_location_placements', blank=True, on_delete=django.db.models.deletion.SET_NULL, to='lib_collections.CollectingAreaPage'),
        ),
    ]
