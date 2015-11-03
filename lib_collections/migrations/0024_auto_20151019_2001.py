# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0023_auto_20151019_1948'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionpage',
            name='access_instructions',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='collectionpage',
            name='full_description',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='collectionpage',
            name='short_abstract',
            field=models.TextField(default=''),
        ),
    ]
