# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0017_auto_20151019_1837'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionpage',
            name='donor2',
            field=models.ManyToManyField(blank=True, to='public.DonorPage'),
        ),
    ]
