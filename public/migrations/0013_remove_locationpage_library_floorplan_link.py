# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0012_floorplanpage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='locationpage',
            name='library_floorplan_link',
        ),
    ]
