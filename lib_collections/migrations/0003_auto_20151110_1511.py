# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0001_initial'),
        ('public', '0002_auto_20151110_1511'),
        ('staff', '0001_initial'),
        ('units', '0001_initial'),
        ('lib_collections', '0002_auto_20151110_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionpage',
            name='unit',
            field=models.ForeignKey(related_name='lib_collections_collectionpage_related', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='units.UnitPage', null=True),
        ),
        migrations.AddField(
            model_name='collectingareareferencelocationplacement',
            name='parent',
            field=modelcluster.fields.ParentalKey(related_name='reference_location_placements', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='lib_collections.CollectingAreaPage', null=True),
        ),
        migrations.AddField(
            model_name='collectingareareferencelocationplacement',
            name='related_collection',
            field=models.ForeignKey(related_name='reference_location', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='public.LocationPage', null=True),
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
            field=models.ForeignKey(related_name='lib_collections_collectingareapage_content_specialist', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='collectingareapage',
            name='editor',
            field=models.ForeignKey(related_name='lib_collections_collectingareapage_editor', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='collectingareapage',
            name='page_maintainer',
            field=models.ForeignKey(related_name='lib_collections_collectingareapage_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='collectingareapage',
            name='subject',
            field=models.ForeignKey(related_name='lib_collections_collectingareapage_related', on_delete=django.db.models.deletion.SET_NULL, to='subjects.Subject', null=True),
        ),
        migrations.AddField(
            model_name='collectingareapage',
            name='unit',
            field=models.ForeignKey(related_name='lib_collections_collectingareapage_related', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='units.UnitPage', null=True),
        ),
    ]
