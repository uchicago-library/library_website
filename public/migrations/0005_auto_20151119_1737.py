# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.models
import wagtail.core.fields
import wagtail.images.blocks
import wagtail.core.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0004_auto_20151118_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standardpage',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow')), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.core.blocks.RichTextBlock()), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image', icon='image')))),
        ),
    ]
