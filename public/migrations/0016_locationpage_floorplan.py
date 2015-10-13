# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0015_auto_20150929_1738'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationpage',
            name='floorplan',
            field=models.URLField(blank=True, default=''),
        ),
    ]
