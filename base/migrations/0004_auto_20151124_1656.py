# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.core.fields
import wagtail.core.blocks
import wagtail.images.blocks
import base.models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_auto_20151118_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intranetplainpage',
            name='body',
            field=wagtail.core.fields.StreamField([(b'h2', wagtail.core.blocks.CharBlock(classname=b'title', template=b'base/blocks/h2.html', icon=b'title')), (b'h3', wagtail.core.blocks.CharBlock(classname=b'title', template=b'base/blocks/h3.html', icon=b'title')), (b'h4', wagtail.core.blocks.CharBlock(classname=b'title', template=b'base/blocks/h4.html', icon=b'title')), (b'h5', wagtail.core.blocks.CharBlock(classname=b'title', template=b'base/blocks/h5.html', icon=b'title')), (b'h6', wagtail.core.blocks.CharBlock(classname=b'title', template=b'base/blocks/h6.html', icon=b'title')), (b'paragraph', wagtail.core.blocks.StructBlock([(b'paragraph', wagtail.core.blocks.RichTextBlock())])), (b'image', wagtail.core.blocks.StructBlock([(b'image', wagtail.images.blocks.ImageChooserBlock()), (b'caption', wagtail.core.blocks.TextBlock(required=False)), (b'citation', wagtail.core.blocks.CharBlock(required=False)), (b'alt_text', wagtail.core.blocks.CharBlock(required=False)), (b'alignment', base.models.ImageFormatChoiceBlock())], label=b'Image')), (b'blockquote', wagtail.core.blocks.StructBlock([(b'quote', wagtail.core.blocks.TextBlock(b'quote title')), (b'attribution', wagtail.core.blocks.CharBlock())]))]),
        ),
        migrations.AlterField(
            model_name='intranetsidebarpage',
            name='body',
            field=wagtail.core.fields.StreamField([(b'h2', wagtail.core.blocks.CharBlock(classname=b'title', template=b'base/blocks/h2.html', icon=b'title')), (b'h3', wagtail.core.blocks.CharBlock(classname=b'title', template=b'base/blocks/h3.html', icon=b'title')), (b'h4', wagtail.core.blocks.CharBlock(classname=b'title', template=b'base/blocks/h4.html', icon=b'title')), (b'h5', wagtail.core.blocks.CharBlock(classname=b'title', template=b'base/blocks/h5.html', icon=b'title')), (b'h6', wagtail.core.blocks.CharBlock(classname=b'title', template=b'base/blocks/h6.html', icon=b'title')), (b'paragraph', wagtail.core.blocks.StructBlock([(b'paragraph', wagtail.core.blocks.RichTextBlock())])), (b'image', wagtail.core.blocks.StructBlock([(b'image', wagtail.images.blocks.ImageChooserBlock()), (b'caption', wagtail.core.blocks.TextBlock(required=False)), (b'citation', wagtail.core.blocks.CharBlock(required=False)), (b'alt_text', wagtail.core.blocks.CharBlock(required=False)), (b'alignment', base.models.ImageFormatChoiceBlock())], label=b'Image')), (b'blockquote', wagtail.core.blocks.StructBlock([(b'quote', wagtail.core.blocks.TextBlock(b'quote title')), (b'attribution', wagtail.core.blocks.CharBlock())]))]),
        ),
    ]
