# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.models
import wagtail.core.blocks
import wagtail.images.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0013_auto_20151124_0007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newspage',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h2.html')), ('h3', wagtail.core.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h3.html')), ('h4', wagtail.core.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h4.html')), ('h5', wagtail.core.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h5.html')), ('h6', wagtail.core.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h6.html')), ('paragraph', wagtail.core.blocks.StructBlock((('paragraph', wagtail.core.blocks.RichTextBlock()),))), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.TextBlock(required=False)), ('citation', wagtail.core.blocks.CharBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image')), ('blockquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock())))))),
        ),
    ]
