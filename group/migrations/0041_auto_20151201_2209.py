# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0040_auto_20151201_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouppage',
            name='show_sidebar',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='grouppage',
            name='subsection_start',
            field=models.BooleanField(default=False),
        ),
    ]
