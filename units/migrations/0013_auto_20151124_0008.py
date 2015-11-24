# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.models
import wagtail.wagtailcore.blocks
import wagtail.wagtailimages.blocks
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0012_auto_20151124_0007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitpage',
            name='body',
            field=wagtail.wagtailcore.fields.StreamField((('h2', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h2.html')), ('h3', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h3.html')), ('h4', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h4.html')), ('h5', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h5.html')), ('h6', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h6.html')), ('paragraph', wagtail.wagtailcore.blocks.StructBlock((('paragraph', wagtail.wagtailcore.blocks.RichTextBlock()),))), ('image', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock()), ('caption', wagtail.wagtailcore.blocks.TextBlock(required=False)), ('citation', wagtail.wagtailcore.blocks.CharBlock(required=False)), ('alt_text', wagtail.wagtailcore.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image')), ('blockquote', wagtail.wagtailcore.blocks.StructBlock((('quote', wagtail.wagtailcore.blocks.TextBlock('quote title')), ('attribution', wagtail.wagtailcore.blocks.CharBlock())))))),
        ),
    ]
