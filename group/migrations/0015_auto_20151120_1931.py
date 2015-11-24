# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.blocks
import base.models
import wagtail.wagtailcore.fields
import datetime
import wagtail.wagtailimages.blocks
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0014_auto_20151120_1930'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouppage',
            name='intro',
            field=wagtail.wagtailcore.fields.StreamField((('h2', wagtail.wagtailcore.blocks.CharBlock(classname='title', template='base/blocks/h2.html', icon='title')), ('h3', wagtail.wagtailcore.blocks.CharBlock(classname='title', template='base/blocks/h3.html', icon='title')), ('h4', wagtail.wagtailcore.blocks.CharBlock(classname='title', template='base/blocks/h4.html', icon='title')), ('h5', wagtail.wagtailcore.blocks.CharBlock(classname='title', template='base/blocks/h5.html', icon='title')), ('h6', wagtail.wagtailcore.blocks.CharBlock(classname='title', template='base/blocks/h6.html', icon='title')), ('paragraph', wagtail.wagtailcore.blocks.StructBlock((('paragraph', wagtail.wagtailcore.blocks.RichTextBlock()),))), ('image', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock()), ('caption', wagtail.wagtailcore.blocks.RichTextBlock()), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image', icon='image')), ('blockquote', wagtail.wagtailcore.blocks.StructBlock((('quote', wagtail.wagtailcore.blocks.TextBlock('quote title')), ('attribution', wagtail.wagtailcore.blocks.CharBlock()))))), blank=True),
        ),
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(blank=True, default=datetime.datetime(2015, 11, 20, 20, 31, 41, 249033, tzinfo=utc)),
        ),
    ]
