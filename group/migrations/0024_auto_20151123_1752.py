# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.models
import wagtail.core.fields
import wagtail.core.blocks
import datetime
from django.utils.timezone import utc
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0023_auto_20151123_1749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppage',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(template='base/blocks/h2.html', icon='title', classname='title')), ('h3', wagtail.core.blocks.CharBlock(template='base/blocks/h3.html', icon='title', classname='title')), ('h4', wagtail.core.blocks.CharBlock(template='base/blocks/h4.html', icon='title', classname='title')), ('h5', wagtail.core.blocks.CharBlock(template='base/blocks/h5.html', icon='title', classname='title')), ('h6', wagtail.core.blocks.CharBlock(template='base/blocks/h6.html', icon='title', classname='title')), ('paragraph', wagtail.core.blocks.StructBlock((('paragraph', wagtail.core.blocks.RichTextBlock()),))), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.TextBlock(required=False)), ('citation', wagtail.core.blocks.CharBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(required=True)), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image', icon='image')), ('blockquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock())))))),
        ),
        migrations.AlterField(
            model_name='grouppage',
            name='intro',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(template='base/blocks/h2.html', icon='title', classname='title')), ('h3', wagtail.core.blocks.CharBlock(template='base/blocks/h3.html', icon='title', classname='title')), ('h4', wagtail.core.blocks.CharBlock(template='base/blocks/h4.html', icon='title', classname='title')), ('h5', wagtail.core.blocks.CharBlock(template='base/blocks/h5.html', icon='title', classname='title')), ('h6', wagtail.core.blocks.CharBlock(template='base/blocks/h6.html', icon='title', classname='title')), ('paragraph', wagtail.core.blocks.StructBlock((('paragraph', wagtail.core.blocks.RichTextBlock()),))), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.TextBlock(required=False)), ('citation', wagtail.core.blocks.CharBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(required=True)), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image', icon='image')), ('blockquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock()))))), blank=True),
        ),
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(default=datetime.datetime(2015, 11, 23, 18, 52, 40, 223152, tzinfo=utc), blank=True),
        ),
    ]
