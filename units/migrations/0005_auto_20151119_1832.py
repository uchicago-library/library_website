# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.fields
import wagtail.images.blocks
import wagtail.blocks
import base.models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0004_auto_20151119_1749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitpage',
            name='body',
            field=wagtail.fields.StreamField((('h2', wagtail.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.blocks.CharBlock(classname='title', icon='title')), ('h5', wagtail.blocks.CharBlock(classname='title', icon='title')), ('h6', wagtail.blocks.CharBlock(classname='title', icon='title')), ('paragraph', wagtail.blocks.RichTextBlock(icon='pilcrow')), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock()), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image', icon='image')), ('blockquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('attribution', wagtail.blocks.CharBlock())))), ('ordered_list', wagtail.blocks.ListBlock(wagtail.blocks.RichTextBlock(), icon='list-ol')), ('unordered_list', wagtail.blocks.ListBlock(wagtail.blocks.RichTextBlock(), icon='list-ul')))),
        ),
    ]
