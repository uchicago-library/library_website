# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20151113_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newspage',
            name='last_reviewed',
            field=models.DateField(blank=True, null=True, verbose_name='Last Reviewed'),
        ),
    ]
