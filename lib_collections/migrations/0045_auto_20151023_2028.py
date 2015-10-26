# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0044_auto_20151023_1951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjectspecialistplacement',
            name='subject_specialist',
            field=models.ForeignKey(to='staff.StaffPage', unique=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subject_specialist', null=True),
        ),
    ]
