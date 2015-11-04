# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0008_grouppagemeetingminutes'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouppage',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='grouppage',
            name='meeting_frequency',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
