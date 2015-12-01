# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0014_auto_20151124_0008'),
    ]

    operations = [
        migrations.AddField(
            model_name='newspage',
            name='show_sidebar',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='newspage',
            name='subsection_start',
            field=models.BooleanField(default=False),
        ),
    ]
