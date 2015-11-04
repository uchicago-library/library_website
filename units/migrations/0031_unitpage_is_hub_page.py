# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0030_unitpagereports'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitpage',
            name='is_hub_page',
            field=models.BooleanField(default=False),
        ),
    ]
