# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0014_locationpage_library_floorplan_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationpage',
            name='is_open_space',
            field=models.BooleanField(default=False),
        ),
    ]
