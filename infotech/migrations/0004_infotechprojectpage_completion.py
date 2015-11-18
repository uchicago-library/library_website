# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infotech', '0003_infotechprojectpage_date_added_to_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='infotechprojectpage',
            name='completion',
            field=models.DateField(null=True, blank=True),
        ),
    ]
