# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0027_auto_20151228_2126'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unitpagereports',
            name='document',
        ),
        migrations.RemoveField(
            model_name='unitpagereports',
            name='link',
        ),
    ]
