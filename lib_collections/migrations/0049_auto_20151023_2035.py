# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0007_remove_staffpage_is_subject_specialist'),
        ('lib_collections', '0048_auto_20151023_2032'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subjectspecialistplacement',
            name='subject_specialist',
        ),
        migrations.AddField(
            model_name='subjectspecialistplacement',
            name='subject_specialist',
            field=models.ForeignKey(related_name='subject_specialist', blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage'),
        ),
    ]
