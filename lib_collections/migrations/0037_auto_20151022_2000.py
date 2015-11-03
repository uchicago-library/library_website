# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0036_auto_20151022_1958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjectspecialistplacement',
            name='parent',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.SET_NULL, related_name='subject_specialist_placement', blank=True, null=True, to='staff.StaffPage'),
        ),
    ]
