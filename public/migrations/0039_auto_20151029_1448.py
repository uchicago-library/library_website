# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0038_auto_20151027_1902'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donorpage',
            name='description',
        ),
        migrations.RemoveField(
            model_name='locationpage',
            name='description',
        ),
        migrations.RemoveField(
            model_name='standardpage',
            name='description',
        ),
    ]
