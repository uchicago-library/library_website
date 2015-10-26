# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0007_remove_staffpage_is_subject_specialist'),
        ('lib_collections', '0046_auto_20151023_2029'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subjectspecialistplacement',
            name='subject_specialist',
        ),
        migrations.AddField(
            model_name='subjectspecialistplacement',
            name='subject_specialist',
            field=models.ManyToManyField(related_name='subject_specialist', to='staff.StaffPage', null=True, blank=True),
        ),
    ]
