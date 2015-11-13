# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0002_auto_20151113_2245'),
        ('subjects', '0001_initial'),
        ('units', '0001_initial'),
        ('staff', '0001_initial'),
        ('lib_collections', '0002_auto_20151113_2245'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionpage',
            name='unit',
            field=models.ForeignKey(to='units.UnitPage', on_delete=django.db.models.deletion.SET_NULL, related_name='lib_collections_collectionpage_related', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='collectingareareferencelocationplacement',
            name='parent',
            field=modelcluster.fields.ParentalKey(to='lib_collections.CollectingAreaPage', on_delete=django.db.models.deletion.SET_NULL, related_name='reference_location_placements', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='collectingareareferencelocationplacement',
            name='related_collection',
            field=models.ForeignKey(to='public.LocationPage', on_delete=django.db.models.deletion.SET_NULL, related_name='reference_location', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='collectingareapagestacksranges',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='stacks_ranges', to='lib_collections.CollectingAreaPage'),
        ),
        migrations.AddField(
            model_name='collectingareapagelibguides',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='lib_guides', to='lib_collections.CollectingAreaPage'),
        ),
        migrations.AddField(
            model_name='collectingareapage',
            name='content_specialist',
            field=models.ForeignKey(to='staff.StaffPage', related_name='lib_collections_collectingareapage_content_specialist', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='collectingareapage',
            name='editor',
            field=models.ForeignKey(to='staff.StaffPage', related_name='lib_collections_collectingareapage_editor', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='collectingareapage',
            name='page_maintainer',
            field=models.ForeignKey(to='staff.StaffPage', related_name='lib_collections_collectingareapage_maintainer', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='collectingareapage',
            name='subject',
            field=models.ForeignKey(to='subjects.Subject', related_name='lib_collections_collectingareapage_related', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='collectingareapage',
            name='unit',
            field=models.ForeignKey(to='units.UnitPage', on_delete=django.db.models.deletion.SET_NULL, related_name='lib_collections_collectingareapage_related', blank=True, null=True),
        ),
    ]
