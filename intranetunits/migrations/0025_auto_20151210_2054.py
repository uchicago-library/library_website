# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('intranetunits', '0024_auto_20151209_2251'),
    ]

    operations = [
        migrations.AddField(
            model_name='intranetunitspage',
            name='show_departments',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='intranetunitspage',
            name='show_staff',
            field=models.BooleanField(default=False),
        ),
    ]
