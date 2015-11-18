# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infotech', '0004_infotechprojectpage_completion'),
    ]

    operations = [
        migrations.AddField(
            model_name='infotechprojectpage',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='infotechprojectpage',
            name='staff',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
