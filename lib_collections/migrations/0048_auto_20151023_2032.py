# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0047_auto_20151023_2032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjectspecialistplacement',
            name='subject_specialist',
            field=models.ManyToManyField(to='staff.StaffPage', blank=True, related_name='subject_specialist'),
        ),
    ]
