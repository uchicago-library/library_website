# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-26 19:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0037_auto_20160708_1033'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionpage',
            name='unit_contact',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='exhibitpage',
            name='unit_contact',
            field=models.BooleanField(default=False),
        ),
    ]