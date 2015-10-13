# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0016_locationpage_floorplan'),
    ]

    operations = [
        migrations.RenameField(
            model_name='locationpage',
            old_name='floorplan',
            new_name='library_floorplan_link',
        ),
    ]
