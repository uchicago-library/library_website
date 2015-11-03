# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0004_auto_20151031_0320'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grouppage',
            name='meeting_time',
        ),
    ]
