# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.core.fields
import wagtail.images.blocks
import wagtail.core.blocks
import base.models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0007_auto_20151119_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitpage',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(template='base/blocks/h2.html', icon='title', classname='title')), ('h3', wagtail.core.blocks.CharBlock(icon='title', classname='title')), ('h4', wagtail.core.blocks.CharBlock(icon='title', classname='title')), ('h5', wagtail.core.blocks.CharBlock(icon='title', classname='title')), ('h6', wagtail.core.blocks.CharBlock(icon='title', classname='title')), ('paragraph', wagtail.core.blocks.StructBlock((('paragraph', wagtail.core.blocks.RichTextBlock()),))), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock()), ('alignment', base.models.ImageFormatChoiceBlock())), icon='image', label='Image')), ('blockquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock())))))),
        ),
    ]
