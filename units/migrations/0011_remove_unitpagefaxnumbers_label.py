# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0010_unitpagefaxnumbers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unitpagefaxnumbers',
            name='label',
        ),
    ]
