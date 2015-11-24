# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.fields
import wagtail.wagtailcore.blocks
import wagtail.wagtailimages.blocks
import base.models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_auto_20151118_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intranetplainpage',
            name='body',
            field=wagtail.wagtailcore.fields.StreamField([(b'h2', wagtail.wagtailcore.blocks.CharBlock(classname=b'title', template=b'base/blocks/h2.html', icon=b'title')), (b'h3', wagtail.wagtailcore.blocks.CharBlock(classname=b'title', template=b'base/blocks/h3.html', icon=b'title')), (b'h4', wagtail.wagtailcore.blocks.CharBlock(classname=b'title', template=b'base/blocks/h4.html', icon=b'title')), (b'h5', wagtail.wagtailcore.blocks.CharBlock(classname=b'title', template=b'base/blocks/h5.html', icon=b'title')), (b'h6', wagtail.wagtailcore.blocks.CharBlock(classname=b'title', template=b'base/blocks/h6.html', icon=b'title')), (b'paragraph', wagtail.wagtailcore.blocks.StructBlock([(b'paragraph', wagtail.wagtailcore.blocks.RichTextBlock())])), (b'image', wagtail.wagtailcore.blocks.StructBlock([(b'image', wagtail.wagtailimages.blocks.ImageChooserBlock()), (b'caption', wagtail.wagtailcore.blocks.TextBlock(required=False)), (b'citation', wagtail.wagtailcore.blocks.CharBlock(required=False)), (b'alt_text', wagtail.wagtailcore.blocks.CharBlock(required=False)), (b'alignment', base.models.ImageFormatChoiceBlock())], label=b'Image')), (b'blockquote', wagtail.wagtailcore.blocks.StructBlock([(b'quote', wagtail.wagtailcore.blocks.TextBlock(b'quote title')), (b'attribution', wagtail.wagtailcore.blocks.CharBlock())]))]),
        ),
        migrations.AlterField(
            model_name='intranetsidebarpage',
            name='body',
            field=wagtail.wagtailcore.fields.StreamField([(b'h2', wagtail.wagtailcore.blocks.CharBlock(classname=b'title', template=b'base/blocks/h2.html', icon=b'title')), (b'h3', wagtail.wagtailcore.blocks.CharBlock(classname=b'title', template=b'base/blocks/h3.html', icon=b'title')), (b'h4', wagtail.wagtailcore.blocks.CharBlock(classname=b'title', template=b'base/blocks/h4.html', icon=b'title')), (b'h5', wagtail.wagtailcore.blocks.CharBlock(classname=b'title', template=b'base/blocks/h5.html', icon=b'title')), (b'h6', wagtail.wagtailcore.blocks.CharBlock(classname=b'title', template=b'base/blocks/h6.html', icon=b'title')), (b'paragraph', wagtail.wagtailcore.blocks.StructBlock([(b'paragraph', wagtail.wagtailcore.blocks.RichTextBlock())])), (b'image', wagtail.wagtailcore.blocks.StructBlock([(b'image', wagtail.wagtailimages.blocks.ImageChooserBlock()), (b'caption', wagtail.wagtailcore.blocks.TextBlock(required=False)), (b'citation', wagtail.wagtailcore.blocks.CharBlock(required=False)), (b'alt_text', wagtail.wagtailcore.blocks.CharBlock(required=False)), (b'alignment', base.models.ImageFormatChoiceBlock())], label=b'Image')), (b'blockquote', wagtail.wagtailcore.blocks.StructBlock([(b'quote', wagtail.wagtailcore.blocks.TextBlock(b'quote title')), (b'attribution', wagtail.wagtailcore.blocks.CharBlock())]))]),
        ),
    ]
