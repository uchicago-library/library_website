# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0023_auto_20151209_2251'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unitpage',
            name='is_hub_page',
        ),
    ]
