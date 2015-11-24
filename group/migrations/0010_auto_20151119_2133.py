# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailimages.blocks
import wagtail.wagtailcore.blocks
import base.models
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0009_auto_20151119_2124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppage',
            name='body',
            field=wagtail.wagtailcore.fields.StreamField((('h2', wagtail.wagtailcore.blocks.CharBlock(template='base/blocks/h2.html', classname='title', icon='title')), ('h3', wagtail.wagtailcore.blocks.CharBlock(template='base/blocks/h3.html', classname='title', icon='title')), ('h4', wagtail.wagtailcore.blocks.CharBlock(template='base/blocks/h4.html', classname='title', icon='title')), ('h5', wagtail.wagtailcore.blocks.CharBlock(template='base/blocks/h5.html', classname='title', icon='title')), ('h6', wagtail.wagtailcore.blocks.CharBlock(template='base/blocks/h6.html', classname='title', icon='title')), ('paragraph', wagtail.wagtailcore.blocks.StructBlock((('paragraph', wagtail.wagtailcore.blocks.RichTextBlock()),))), ('image', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock()), ('caption', wagtail.wagtailcore.blocks.RichTextBlock()), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image', icon='image')), ('blockquote', wagtail.wagtailcore.blocks.StructBlock((('quote', wagtail.wagtailcore.blocks.TextBlock('quote title')), ('attribution', wagtail.wagtailcore.blocks.CharBlock())))))),
        ),
    ]
