# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0019_verbose_names_cleanup'),
        ('units', '0014_remove_unitpage_public_web_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitpage',
            name='public_web_page',
            field=models.ForeignKey(to='wagtailcore.Page', related_name='+', null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
