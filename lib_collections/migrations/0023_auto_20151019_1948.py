# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0022_collectionpagealternatenames'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionpagealternatenames',
            name='alternate_name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
