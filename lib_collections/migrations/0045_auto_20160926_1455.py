# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-26 19:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0044_auto_20160920_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='exhibitpage',
            name='font_family',
            field=models.CharField(blank=True, help_text="CSS font-family value, e.g. 'Roboto', sans-serif", max_length=100),
        ),
        migrations.AddField(
            model_name='exhibitpage',
            name='google_font_link',
            field=models.URLField(blank=True, help_text='Google fonts link to embedd in the header'),
        ),
    ]
