# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0005_staffpagesubjectplacement'),
        ('lib_collections', '0039_remove_subjectspecialistplacement_subject_specialist'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjectspecialistplacement',
            name='subject_specialist',
            field=models.ForeignKey(blank=True, to='staff.StaffPage', on_delete=django.db.models.deletion.SET_NULL, null=True, related_name='subject_specialist'),
        ),
    ]
