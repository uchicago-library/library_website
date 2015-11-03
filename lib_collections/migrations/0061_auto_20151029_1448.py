# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0060_collectingareapagelibguides'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collectingareapage',
            name='description',
        ),
        migrations.RemoveField(
            model_name='collectionpage',
            name='description',
        ),
    ]
