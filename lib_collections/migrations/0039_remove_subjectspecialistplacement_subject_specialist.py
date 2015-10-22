# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0038_auto_20151022_2011'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subjectspecialistplacement',
            name='subject_specialist',
        ),
    ]
