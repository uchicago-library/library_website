# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0006_add_verbose_names'),
        ('public', '0017_auto_20150929_2117'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationpage',
            name='location_photo',
            field=models.ForeignKey(null=True, to='wagtailimages.Image', on_delete=django.db.models.deletion.SET_NULL, blank=True, related_name='+'),
        ),
    ]
