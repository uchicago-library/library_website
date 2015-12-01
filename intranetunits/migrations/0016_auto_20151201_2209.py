# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('intranetunits', '0015_auto_20151125_2046'),
    ]

    operations = [
        migrations.AddField(
            model_name='intranetunitspage',
            name='show_sidebar',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='intranetunitspage',
            name='subsection_start',
            field=models.BooleanField(default=False),
        ),
    ]
