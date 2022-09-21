# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.models
import wagtail.fields
import wagtail.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0010_auto_20151123_1749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitpage',
            name='body',
            field=wagtail.fields.StreamField((('h2', wagtail.blocks.CharBlock(template='base/blocks/h2.html', icon='title', classname='title')), ('h3', wagtail.blocks.CharBlock(template='base/blocks/h3.html', icon='title', classname='title')), ('h4', wagtail.blocks.CharBlock(template='base/blocks/h4.html', icon='title', classname='title')), ('h5', wagtail.blocks.CharBlock(template='base/blocks/h5.html', icon='title', classname='title')), ('h6', wagtail.blocks.CharBlock(template='base/blocks/h6.html', icon='title', classname='title')), ('paragraph', wagtail.blocks.StructBlock((('paragraph', wagtail.blocks.RichTextBlock()),))), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.TextBlock(required=False)), ('citation', wagtail.blocks.CharBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=True)), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image', icon='image')), ('blockquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('attribution', wagtail.blocks.CharBlock())))))),
        ),
    ]
