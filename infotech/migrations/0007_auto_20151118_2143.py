# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infotech', '0006_infotechindexpage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='infotechprojectpage',
            name='last_reviewed',
            field=models.DateField(blank=True, null=True, verbose_name='Last Reviewed'),
        ),
    ]
