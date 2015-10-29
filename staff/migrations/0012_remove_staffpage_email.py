# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0011_staffpagepagevcards'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staffpage',
            name='email',
        ),
    ]
