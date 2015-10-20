# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0025_donorpage'),
        ('lib_collections', '0015_donorpagelistplacement'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionpage',
            name='donor2',
            field=models.ManyToManyField(to='public.DonorPage'),
        ),
    ]
