# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_auto_20151104_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newspage',
            name='sticky_until',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
