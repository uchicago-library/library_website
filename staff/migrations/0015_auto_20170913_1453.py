# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-09-13 19:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0014_auto_20170913_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffpage',
            name='profile_picture',
            field=models.ForeignKey(blank=True, help_text='Profile pictures should be frontal headshots, preferrably on a gray background.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image'),
        ),
    ]
