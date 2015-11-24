# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import base.models
import wagtail.wagtailcore.fields
import wagtail.wagtailimages.blocks
import wagtail.wagtailcore.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('intranetunits', '0003_auto_20151118_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intranetunitspage',
            name='body',
            field=wagtail.wagtailcore.fields.StreamField((('h2', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), ('paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow')), ('image', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock()), ('caption', wagtail.wagtailcore.blocks.RichTextBlock()), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image', icon='image'))), null=True, blank=True),
        ),
    ]
