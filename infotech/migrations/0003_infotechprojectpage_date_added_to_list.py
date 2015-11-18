# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('infotech', '0002_auto_20151118_2106'),
    ]

    operations = [
        migrations.AddField(
            model_name='infotechprojectpage',
            name='date_added_to_list',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
