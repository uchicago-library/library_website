# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.core.blocks
import base.models
import wagtail.core.fields
import datetime
import wagtail.images.blocks
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0014_auto_20151120_1930'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouppage',
            name='intro',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', template='base/blocks/h2.html', icon='title')), ('h3', wagtail.core.blocks.CharBlock(classname='title', template='base/blocks/h3.html', icon='title')), ('h4', wagtail.core.blocks.CharBlock(classname='title', template='base/blocks/h4.html', icon='title')), ('h5', wagtail.core.blocks.CharBlock(classname='title', template='base/blocks/h5.html', icon='title')), ('h6', wagtail.core.blocks.CharBlock(classname='title', template='base/blocks/h6.html', icon='title')), ('paragraph', wagtail.core.blocks.StructBlock((('paragraph', wagtail.core.blocks.RichTextBlock()),))), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock()), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image', icon='image')), ('blockquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock()))))), blank=True),
        ),
        migrations.AlterField(
            model_name='grouppage',
            name='meeting_end_time',
            field=models.TimeField(blank=True, default=datetime.datetime(2015, 11, 20, 20, 31, 41, 249033, tzinfo=utc)),
        ),
    ]
