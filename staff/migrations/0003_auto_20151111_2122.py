# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0002_auto_20151111_2026'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staffpage',
            name='editor',
        ),
        migrations.RemoveField(
            model_name='staffpage',
            name='last_reviewed',
        ),
        migrations.RemoveField(
            model_name='staffpage',
            name='page_maintainer',
        ),
        migrations.AlterField(
            model_name='staffpage',
            name='bio',
            field=wagtail.wagtailcore.fields.RichTextField(default=''),
            preserve_default=False,
        ),
    ]
