# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.images.blocks
import wagtail.core.fields
import base.models
import wagtail.core.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20151124_1656'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intranetplainpage',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(template='base/blocks/h2.html', classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(template='base/blocks/h3.html', classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(template='base/blocks/h4.html', classname='title', icon='title')), ('h5', wagtail.core.blocks.CharBlock(template='base/blocks/h5.html', classname='title', icon='title')), ('h6', wagtail.core.blocks.CharBlock(template='base/blocks/h6.html', classname='title', icon='title')), ('paragraph', wagtail.core.blocks.StructBlock((('paragraph', wagtail.core.blocks.RichTextBlock()),))), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.TextBlock(required=False)), ('citation', wagtail.core.blocks.CharBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image')), ('blockquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock())))))),
        ),
        migrations.AlterField(
            model_name='intranetsidebarpage',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(template='base/blocks/h2.html', classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(template='base/blocks/h3.html', classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(template='base/blocks/h4.html', classname='title', icon='title')), ('h5', wagtail.core.blocks.CharBlock(template='base/blocks/h5.html', classname='title', icon='title')), ('h6', wagtail.core.blocks.CharBlock(template='base/blocks/h6.html', classname='title', icon='title')), ('paragraph', wagtail.core.blocks.StructBlock((('paragraph', wagtail.core.blocks.RichTextBlock()),))), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.TextBlock(required=False)), ('citation', wagtail.core.blocks.CharBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image')), ('blockquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock())))))),
        ),
    ]
