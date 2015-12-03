# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0014_unitindexpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitpage',
            name='show_sidebar',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='unitpage',
            name='subsection_start',
            field=models.BooleanField(default=False),
        ),
    ]
