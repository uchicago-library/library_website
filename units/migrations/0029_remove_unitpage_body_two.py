# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0028_unitpage_body'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unitpage',
            name='body_two',
        ),
    ]
