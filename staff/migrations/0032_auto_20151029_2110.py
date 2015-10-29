# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0031_auto_20151029_1915'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffpage',
            name='first_name',
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='staffpage',
            name='last_name',
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='staffpage',
            name='middle_name',
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
    ]
