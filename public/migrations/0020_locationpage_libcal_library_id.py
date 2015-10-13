# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0019_auto_20151001_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationpage',
            name='libcal_library_id',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
