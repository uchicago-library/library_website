# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0037_auto_20151022_1854'),
        ('lib_collections', '0051_collectingareapagestacksranges'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectingAreaReferenceLocationPlacement',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('sort_order', models.IntegerField(editable=False, null=True, blank=True)),
                ('parent', modelcluster.fields.ParentalKey(null=True, to='lib_collections.CollectingAreaPage', related_name='reference_location_placement', on_delete=django.db.models.deletion.SET_NULL, blank=True)),
                ('related_collection', models.ForeignKey(null=True, to='public.LocationPage', related_name='reference_location', on_delete=django.db.models.deletion.SET_NULL, blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
    ]
