# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0013_unitpage_public_web_page'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unitpage',
            name='public_web_page',
        ),
    ]
