# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0008_image_created_at_index'),
        ('public', '0041_auto_20151029_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='donorpage',
            name='image',
            field=models.ForeignKey(related_name='+', blank=True, on_delete=django.db.models.deletion.SET_NULL, to='wagtailimages.Image', null=True),
        ),
    ]
