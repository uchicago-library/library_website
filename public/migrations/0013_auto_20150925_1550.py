# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0012_locationpage_standardpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationpage',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='public.LocationPage', null=True),
        ),
        migrations.AddField(
            model_name='standardpage',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='public.LocationPage', null=True),
        ),
    ]
