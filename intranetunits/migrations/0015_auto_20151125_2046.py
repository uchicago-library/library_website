# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.images.blocks
import django.db.models.deletion
import wagtail.blocks
import base.models
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('intranetunits', '0014_auto_20151124_0008'),
    ]

    operations = [
        migrations.AddField(
            model_name='intranetunitspage',
            name='unit',
            field=models.ForeignKey(related_name='intranet_unit_page', blank=True, to='units.UnitPage', null=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='intranetunitspage',
            name='intro',
            field=wagtail.fields.StreamField((('h2', wagtail.blocks.CharBlock(icon='title', template='base/blocks/h2.html', classname='title')), ('h3', wagtail.blocks.CharBlock(icon='title', template='base/blocks/h3.html', classname='title')), ('h4', wagtail.blocks.CharBlock(icon='title', template='base/blocks/h4.html', classname='title')), ('h5', wagtail.blocks.CharBlock(icon='title', template='base/blocks/h5.html', classname='title')), ('h6', wagtail.blocks.CharBlock(icon='title', template='base/blocks/h6.html', classname='title')), ('paragraph', wagtail.blocks.StructBlock((('paragraph', wagtail.blocks.RichTextBlock()),))), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.TextBlock(required=False)), ('citation', wagtail.blocks.CharBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image')), ('blockquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('attribution', wagtail.blocks.CharBlock()))))), blank=True),
        ),
    ]
