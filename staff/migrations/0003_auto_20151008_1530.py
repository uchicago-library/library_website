# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0002_auto_20151008_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffpage',
            name='libguide_url',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
