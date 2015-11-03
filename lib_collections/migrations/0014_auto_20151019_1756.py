# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0013_collectionpage_donor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionpage',
            name='donor',
            field=models.ForeignKey(to='public.DonorPage', related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True),
        ),
    ]
