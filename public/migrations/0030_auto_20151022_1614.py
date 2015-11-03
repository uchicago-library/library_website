# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0029_auto_20151021_2131'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationpage',
            name='address_1',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='address_2',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='city',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='country',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='postal_code',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
