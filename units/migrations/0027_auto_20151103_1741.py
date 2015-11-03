# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0026_remove_unitpage_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='unitpage',
            old_name='body',
            new_name='body_two',
        ),
    ]
