# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0016_collectionpage_donor2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionpage',
            name='donor2',
            field=models.ManyToManyField(to='public.DonorPage', null=True, blank=True),
        ),
    ]
