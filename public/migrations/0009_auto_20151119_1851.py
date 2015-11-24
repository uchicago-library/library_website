# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.blocks
import base.models
import wagtail.wagtailcore.fields
import wagtail.wagtailimages.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0008_auto_20151119_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standardpage',
            name='body',
            field=wagtail.wagtailcore.fields.StreamField((('h2', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title')), ('h3', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title')), ('h4', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title')), ('h5', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title')), ('h6', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title')), ('paragraph', wagtail.wagtailcore.blocks.StructBlock((('paragraph', wagtail.wagtailcore.blocks.RichTextBlock()),))), ('image', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock()), ('caption', wagtail.wagtailcore.blocks.RichTextBlock()), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image', icon='image')), ('blockquote', wagtail.wagtailcore.blocks.StructBlock((('quote', wagtail.wagtailcore.blocks.TextBlock('quote title')), ('attribution', wagtail.wagtailcore.blocks.CharBlock())))))),
        ),
    ]
