# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0012_unitpage_room_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitpage',
            name='public_web_page',
            field=models.URLField(blank=True, default=''),
        ),
    ]
