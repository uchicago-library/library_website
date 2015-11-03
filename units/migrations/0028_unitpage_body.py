# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.blocks
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0027_auto_20151103_1741'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitpage',
            name='body',
            field=wagtail.wagtailcore.fields.StreamField((('h2', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title')), ('h3', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title')), ('h4', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title')), ('paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow'))), default=''),
            preserve_default=False,
        ),
    ]
