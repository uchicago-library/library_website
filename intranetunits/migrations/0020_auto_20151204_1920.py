# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.core.fields
import base.models
import wagtail.images.blocks
import wagtail.core.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('intranetunits', '0019_auto_20151203_2137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intranetunitspage',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(template='base/blocks/h2.html', classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(template='base/blocks/h3.html', classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(template='base/blocks/h4.html', classname='title', icon='title')), ('h5', wagtail.core.blocks.CharBlock(template='base/blocks/h5.html', classname='title', icon='title')), ('h6', wagtail.core.blocks.CharBlock(template='base/blocks/h6.html', classname='title', icon='title')), ('paragraph', wagtail.core.blocks.StructBlock((('paragraph', wagtail.core.blocks.RichTextBlock()),))), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('citation', wagtail.core.blocks.CharBlock(required=False)), ('caption', wagtail.core.blocks.TextBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock()), ('source', wagtail.core.blocks.CharBlock(required=False))), label='Image')), ('blockquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock()))))), blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='intranetunitspage',
            name='intro',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(template='base/blocks/h2.html', classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(template='base/blocks/h3.html', classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(template='base/blocks/h4.html', classname='title', icon='title')), ('h5', wagtail.core.blocks.CharBlock(template='base/blocks/h5.html', classname='title', icon='title')), ('h6', wagtail.core.blocks.CharBlock(template='base/blocks/h6.html', classname='title', icon='title')), ('paragraph', wagtail.core.blocks.StructBlock((('paragraph', wagtail.core.blocks.RichTextBlock()),))), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('citation', wagtail.core.blocks.CharBlock(required=False)), ('caption', wagtail.core.blocks.TextBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock()), ('source', wagtail.core.blocks.CharBlock(required=False))), label='Image')), ('blockquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock()))))), blank=True),
        ),
    ]
