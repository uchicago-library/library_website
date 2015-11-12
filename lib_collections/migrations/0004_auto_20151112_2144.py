# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0003_auto_20151111_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectingareapage',
            name='sort_order',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='collectionpage',
            name='sort_order',
            field=models.IntegerField(default=0, blank=True),
        ),
    ]
