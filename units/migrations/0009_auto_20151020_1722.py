# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0008_auto_20151020_1713'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitpage',
            name='contact_url',
            field=models.URLField(default='', blank=True),
        ),
        migrations.AddField(
            model_name='unitpage',
            name='email',
            field=models.EmailField(max_length=254, blank=True),
        ),
    ]
