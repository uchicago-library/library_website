# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20151201_2144'),
    ]

    operations = [
        migrations.AddField(
            model_name='intranetplainpage',
            name='show_sidebar',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='intranetplainpage',
            name='subsection_start',
            field=models.BooleanField(default=False),
        ),
    ]
