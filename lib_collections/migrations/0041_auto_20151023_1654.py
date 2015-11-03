# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0040_subjectspecialistplacement_subject_specialist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjectspecialistplacement',
            name='subject_specialist',
            field=models.ForeignKey(related_name='subject_specialist', to='staff.StaffPageSubjectPlacement', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True),
        ),
    ]
