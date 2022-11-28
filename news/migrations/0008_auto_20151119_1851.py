# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.blocks
import base.models
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0007_auto_20151119_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newspage',
            name='body',
            field=wagtail.fields.StreamField((('h2', wagtail.blocks.CharBlock(icon='title', classname='title')), ('h3', wagtail.blocks.CharBlock(icon='title', classname='title')), ('h4', wagtail.blocks.CharBlock(icon='title', classname='title')), ('h5', wagtail.blocks.CharBlock(icon='title', classname='title')), ('h6', wagtail.blocks.CharBlock(icon='title', classname='title')), ('paragraph', wagtail.blocks.StructBlock((('paragraph', wagtail.blocks.RichTextBlock()),))), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock()), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image', icon='image')), ('blockquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('attribution', wagtail.blocks.CharBlock())))))),
        ),
    ]
