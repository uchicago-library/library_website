# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitpage',
            name='last_reviewed',
            field=models.DateField(blank=True, null=True, verbose_name='Last Reviewed'),
        ),
    ]
