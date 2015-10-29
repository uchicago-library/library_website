# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0021_auto_20151029_1825'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staffpagepagevcards',
            name='phone_label',
        ),
        migrations.RemoveField(
            model_name='staffpagepagevcards',
            name='phone_number',
        ),
    ]
