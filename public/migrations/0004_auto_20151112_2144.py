# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0003_auto_20151111_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='donorpage',
            name='sort_order',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='sort_order',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='standardpage',
            name='sort_order',
            field=models.IntegerField(default=0, blank=True),
        ),
    ]
