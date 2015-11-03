# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.blocks
import base.models
import wagtail.wagtailimages.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0044_remove_standardpage_body'),
    ]

    operations = [
        migrations.AddField(
            model_name='standardpage',
            name='body',
            field=base.models.DefaultBodyField((('heading', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='full title')), ('paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow')), ('image', wagtail.wagtailimages.blocks.ImageChooserBlock(icon='image / picture'))), default=''),
            preserve_default=False,
        ),
    ]
