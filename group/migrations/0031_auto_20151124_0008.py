# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.images.blocks
import wagtail.core.fields
import base.models
from django.utils.timezone import utc
import datetime
import wagtail.core.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0030_auto_20151124_0007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppage',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h2.html')), ('h3', wagtail.core.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h3.html')), ('h4', wagtail.core.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h4.html')), ('h5', wagtail.core.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h5.html')), ('h6', wagtail.core.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h6.html')), ('paragraph', wagtail.core.blocks.StructBlock((('paragraph', wagtail.core.blocks.RichTextBlock()),))), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.TextBlock(required=False)), ('citation', wagtail.core.blocks.CharBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image')), ('blockquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock())))))),
        ),
        migrations.AlterField(
            model_name='grouppage',
            name='intro',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h2.html')), ('h3', wagtail.core.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h3.html')), ('h4', wagtail.core.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h4.html')), ('h5', wagtail.core.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h5.html')), ('h6', wagtail.core.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h6.html')), ('paragraph', wagtail.core.blocks.StructBlock((('paragraph', wagtail.core.blocks.RichTextBlock()),))), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.TextBlock(required=False)), ('citation', wagtail.core.blocks.CharBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image')), ('blockquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock()))))), blank=True),
        ),
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(blank=True, default=datetime.datetime(2015, 11, 24, 1, 8, 55, 268729, tzinfo=utc)),
        ),
    ]
