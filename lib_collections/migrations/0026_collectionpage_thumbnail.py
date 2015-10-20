# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0008_image_created_at_index'),
        ('lib_collections', '0025_auto_20151019_2003'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionpage',
            name='thumbnail',
            field=models.ForeignKey(to='wagtailimages.Image', blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', null=True),
        ),
    ]
