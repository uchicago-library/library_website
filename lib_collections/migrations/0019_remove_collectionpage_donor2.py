# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0018_auto_20151019_1838'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collectionpage',
            name='donor2',
        ),
    ]
