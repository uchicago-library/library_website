# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-09-13 19:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0016_auto_20170913_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffpage',
            name='supervises_students',
            field=models.BooleanField(default=False, help_text='For HR reporting.'),
        ),
    ]
