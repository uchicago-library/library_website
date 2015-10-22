# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0021_auto_20151022_1813'),
    ]

    operations = [
        migrations.RenameField(
            model_name='unitpagephonenumbers',
            old_name='label',
            new_name='phone_label',
        ),
        migrations.RenameField(
            model_name='unitpagephonenumbers',
            old_name='number',
            new_name='phone_number',
        ),
    ]
