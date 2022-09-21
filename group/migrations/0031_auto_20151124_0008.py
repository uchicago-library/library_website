# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.images.blocks
import wagtail.fields
import base.models
from django.utils.timezone import utc
import datetime
import wagtail.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0030_auto_20151124_0007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppage',
            name='body',
            field=wagtail.fields.StreamField((('h2', wagtail.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h2.html')), ('h3', wagtail.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h3.html')), ('h4', wagtail.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h4.html')), ('h5', wagtail.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h5.html')), ('h6', wagtail.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h6.html')), ('paragraph', wagtail.blocks.StructBlock((('paragraph', wagtail.blocks.RichTextBlock()),))), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.TextBlock(required=False)), ('citation', wagtail.blocks.CharBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image')), ('blockquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('attribution', wagtail.blocks.CharBlock())))))),
        ),
        migrations.AlterField(
            model_name='grouppage',
            name='intro',
            field=wagtail.fields.StreamField((('h2', wagtail.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h2.html')), ('h3', wagtail.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h3.html')), ('h4', wagtail.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h4.html')), ('h5', wagtail.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h5.html')), ('h6', wagtail.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h6.html')), ('paragraph', wagtail.blocks.StructBlock((('paragraph', wagtail.blocks.RichTextBlock()),))), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.TextBlock(required=False)), ('citation', wagtail.blocks.CharBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image')), ('blockquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('attribution', wagtail.blocks.CharBlock()))))), blank=True),
        ),
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(blank=True, default=datetime.datetime(2015, 11, 24, 1, 8, 55, 268729, tzinfo=utc)),
        ),
    ]
