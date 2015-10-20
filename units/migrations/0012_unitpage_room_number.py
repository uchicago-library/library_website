# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0011_remove_unitpagefaxnumbers_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitpage',
            name='room_number',
            field=models.CharField(blank=True, max_length=32),
        ),
    ]
