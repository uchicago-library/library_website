# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0005_format'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionpage',
            name='format',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', blank=True, to='lib_collections.Format'),
        ),
    ]
