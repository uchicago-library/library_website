# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0037_auto_20151022_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjectspecialistplacement',
            name='parent',
            field=modelcluster.fields.ParentalKey(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='lib_collections.CollectingAreaPage', related_name='subject_specialist_placement'),
        ),
        migrations.AlterField(
            model_name='subjectspecialistplacement',
            name='subject_specialist',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='staff.StaffPage', related_name='subject_specialist'),
        ),
    ]
