# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0037_auto_20151031_0320'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grouppageplacement',
            name='group_or_committee',
        ),
        migrations.RemoveField(
            model_name='grouppageplacement',
            name='parent',
        ),
        migrations.DeleteModel(
            name='GroupPagePlacement',
        ),
    ]
