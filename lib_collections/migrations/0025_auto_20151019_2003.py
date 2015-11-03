# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0024_auto_20151019_2001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionpage',
            name='access_instructions',
            field=models.TextField(default='', blank=True),
        ),
    ]
