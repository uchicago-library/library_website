# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0002_auto_20150925_2129'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grouppage',
            name='acronym',
        ),
        migrations.RemoveField(
            model_name='grouppage',
            name='chair',
        ),
        migrations.AddField(
            model_name='grouppage',
            name='name',
            field=models.TextField(blank=True),
        ),
    ]
