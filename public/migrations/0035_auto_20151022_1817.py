# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0034_auto_20151022_1746'),
    ]

    operations = [
        migrations.RenameField(
            model_name='locationpage',
            old_name='label',
            new_name='phone_label',
        ),
        migrations.RenameField(
            model_name='locationpage',
            old_name='number',
            new_name='phone_number',
        ),
    ]
