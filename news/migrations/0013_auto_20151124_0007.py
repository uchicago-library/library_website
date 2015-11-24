# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailimages.blocks
import wagtail.wagtailcore.blocks
import base.models
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0012_auto_20151123_1752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newspage',
            name='body',
            field=wagtail.wagtailcore.fields.StreamField((('h2', wagtail.wagtailcore.blocks.CharBlock(classname='title', template='base/blocks/h2.html', icon='title')), ('h3', wagtail.wagtailcore.blocks.CharBlock(classname='title', template='base/blocks/h3.html', icon='title')), ('h4', wagtail.wagtailcore.blocks.CharBlock(classname='title', template='base/blocks/h4.html', icon='title')), ('h5', wagtail.wagtailcore.blocks.CharBlock(classname='title', template='base/blocks/h5.html', icon='title')), ('h6', wagtail.wagtailcore.blocks.CharBlock(classname='title', template='base/blocks/h6.html', icon='title')), ('paragraph', wagtail.wagtailcore.blocks.StructBlock((('paragraph', wagtail.wagtailcore.blocks.RichTextBlock()),))), ('image', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock()), ('caption', wagtail.wagtailcore.blocks.TextBlock(required=False)), ('citation', wagtail.wagtailcore.blocks.CharBlock(required=False)), ('alt_text', wagtail.wagtailcore.blocks.CharBlock(required=True)), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image')), ('blockquote', wagtail.wagtailcore.blocks.StructBlock((('quote', wagtail.wagtailcore.blocks.TextBlock('quote title')), ('attribution', wagtail.wagtailcore.blocks.CharBlock())))))),
        ),
    ]
