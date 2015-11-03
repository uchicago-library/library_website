# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0019_verbose_names_cleanup'),
        ('lib_collections', '0012_remove_collectionpage_donor'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionpage',
            name='donor',
            field=models.ForeignKey(to='wagtailcore.Page', related_name='+', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True),
        ),
    ]
