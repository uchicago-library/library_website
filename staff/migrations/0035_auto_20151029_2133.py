# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0034_staffpage_supervisor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffpage',
            name='libguide_url',
            field=models.URLField(null=True, max_length=255, blank=True),
        ),
    ]
