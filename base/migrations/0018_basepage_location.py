# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0009_locationpage'),
        ('base', '0017_basepage_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='basepage',
            name='location',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True, to='public.LocationPage'),
        ),
    ]
