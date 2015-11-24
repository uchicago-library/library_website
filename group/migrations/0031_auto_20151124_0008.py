# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailimages.blocks
import wagtail.wagtailcore.fields
import base.models
from django.utils.timezone import utc
import datetime
import wagtail.wagtailcore.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0030_auto_20151124_0007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppage',
            name='body',
            field=wagtail.wagtailcore.fields.StreamField((('h2', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h2.html')), ('h3', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h3.html')), ('h4', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h4.html')), ('h5', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h5.html')), ('h6', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h6.html')), ('paragraph', wagtail.wagtailcore.blocks.StructBlock((('paragraph', wagtail.wagtailcore.blocks.RichTextBlock()),))), ('image', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock()), ('caption', wagtail.wagtailcore.blocks.TextBlock(required=False)), ('citation', wagtail.wagtailcore.blocks.CharBlock(required=False)), ('alt_text', wagtail.wagtailcore.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image')), ('blockquote', wagtail.wagtailcore.blocks.StructBlock((('quote', wagtail.wagtailcore.blocks.TextBlock('quote title')), ('attribution', wagtail.wagtailcore.blocks.CharBlock())))))),
        ),
        migrations.AlterField(
            model_name='grouppage',
            name='intro',
            field=wagtail.wagtailcore.fields.StreamField((('h2', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h2.html')), ('h3', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h3.html')), ('h4', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h4.html')), ('h5', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h5.html')), ('h6', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title', template='base/blocks/h6.html')), ('paragraph', wagtail.wagtailcore.blocks.StructBlock((('paragraph', wagtail.wagtailcore.blocks.RichTextBlock()),))), ('image', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock()), ('caption', wagtail.wagtailcore.blocks.TextBlock(required=False)), ('citation', wagtail.wagtailcore.blocks.CharBlock(required=False)), ('alt_text', wagtail.wagtailcore.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image')), ('blockquote', wagtail.wagtailcore.blocks.StructBlock((('quote', wagtail.wagtailcore.blocks.TextBlock('quote title')), ('attribution', wagtail.wagtailcore.blocks.CharBlock()))))), blank=True),
        ),
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(blank=True, default=datetime.datetime(2015, 11, 24, 1, 8, 55, 268729, tzinfo=utc)),
        ),
    ]
