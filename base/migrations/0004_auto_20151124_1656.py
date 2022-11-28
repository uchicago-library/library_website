# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.fields
import wagtail.blocks
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
            field=wagtail.fields.StreamField([(b'h2', wagtail.blocks.CharBlock(classname=b'title', template=b'base/blocks/h2.html', icon=b'title')), (b'h3', wagtail.blocks.CharBlock(classname=b'title', template=b'base/blocks/h3.html', icon=b'title')), (b'h4', wagtail.blocks.CharBlock(classname=b'title', template=b'base/blocks/h4.html', icon=b'title')), (b'h5', wagtail.blocks.CharBlock(classname=b'title', template=b'base/blocks/h5.html', icon=b'title')), (b'h6', wagtail.blocks.CharBlock(classname=b'title', template=b'base/blocks/h6.html', icon=b'title')), (b'paragraph', wagtail.blocks.StructBlock([(b'paragraph', wagtail.blocks.RichTextBlock())])), (b'image', wagtail.blocks.StructBlock([(b'image', wagtail.images.blocks.ImageChooserBlock()), (b'caption', wagtail.blocks.TextBlock(required=False)), (b'citation', wagtail.blocks.CharBlock(required=False)), (b'alt_text', wagtail.blocks.CharBlock(required=False)), (b'alignment', base.models.ImageFormatChoiceBlock())], label=b'Image')), (b'blockquote', wagtail.blocks.StructBlock([(b'quote', wagtail.blocks.TextBlock(b'quote title')), (b'attribution', wagtail.blocks.CharBlock())]))]),
        ),
        migrations.AlterField(
            model_name='intranetsidebarpage',
            name='body',
            field=wagtail.fields.StreamField([(b'h2', wagtail.blocks.CharBlock(classname=b'title', template=b'base/blocks/h2.html', icon=b'title')), (b'h3', wagtail.blocks.CharBlock(classname=b'title', template=b'base/blocks/h3.html', icon=b'title')), (b'h4', wagtail.blocks.CharBlock(classname=b'title', template=b'base/blocks/h4.html', icon=b'title')), (b'h5', wagtail.blocks.CharBlock(classname=b'title', template=b'base/blocks/h5.html', icon=b'title')), (b'h6', wagtail.blocks.CharBlock(classname=b'title', template=b'base/blocks/h6.html', icon=b'title')), (b'paragraph', wagtail.blocks.StructBlock([(b'paragraph', wagtail.blocks.RichTextBlock())])), (b'image', wagtail.blocks.StructBlock([(b'image', wagtail.images.blocks.ImageChooserBlock()), (b'caption', wagtail.blocks.TextBlock(required=False)), (b'citation', wagtail.blocks.CharBlock(required=False)), (b'alt_text', wagtail.blocks.CharBlock(required=False)), (b'alignment', base.models.ImageFormatChoiceBlock())], label=b'Image')), (b'blockquote', wagtail.blocks.StructBlock([(b'quote', wagtail.blocks.TextBlock(b'quote title')), (b'attribution', wagtail.blocks.CharBlock())]))]),
        ),
    ]
