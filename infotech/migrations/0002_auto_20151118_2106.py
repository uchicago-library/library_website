# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infotech', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='infotechprojectpage',
            name='size',
            field=models.CharField(default='small', max_length=55, choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')]),
        ),
        migrations.AlterField(
            model_name='infotechprojectpage',
            name='status',
            field=models.CharField(default='active', max_length=55, choices=[('active', 'Active'), ('pending', 'Pending'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('discussion', 'Discussion')]),
        ),
    ]
