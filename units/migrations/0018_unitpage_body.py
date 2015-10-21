# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.blocks
import wagtail.wagtailimages.blocks
import base.models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0017_unitpage_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='unitpage',
            name='body',
            field=base.models.DefaultBodyField((('heading', wagtail.wagtailcore.blocks.CharBlock(classname='full title', icon='title')), ('paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow')), ('image', wagtail.wagtailimages.blocks.ImageChooserBlock(icon='image / picture'))), null=True, blank=True),
        ),
    ]
