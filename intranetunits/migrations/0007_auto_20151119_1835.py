# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.models
import wagtail.fields
import wagtail.images.blocks
import wagtail.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('intranetunits', '0006_auto_20151119_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intranetunitspage',
            name='body',
            field=wagtail.fields.StreamField((('h2', wagtail.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.blocks.CharBlock(classname='title', icon='title')), ('h5', wagtail.blocks.CharBlock(classname='title', icon='title')), ('h6', wagtail.blocks.CharBlock(classname='title', icon='title')), ('paragraph', wagtail.blocks.RichTextBlock(icon='pilcrow')), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.RichTextBlock()), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image', icon='image')), ('blockquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('attribution', wagtail.blocks.CharBlock()))))), blank=True, null=True),
        ),
    ]
