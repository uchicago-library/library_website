# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailimages.blocks
import django.db.models.deletion
import wagtail.wagtailcore.blocks
import base.models
import wagtail.wagtailcore.fields


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
            field=wagtail.wagtailcore.fields.StreamField((('h2', wagtail.wagtailcore.blocks.CharBlock(icon='title', template='base/blocks/h2.html', classname='title')), ('h3', wagtail.wagtailcore.blocks.CharBlock(icon='title', template='base/blocks/h3.html', classname='title')), ('h4', wagtail.wagtailcore.blocks.CharBlock(icon='title', template='base/blocks/h4.html', classname='title')), ('h5', wagtail.wagtailcore.blocks.CharBlock(icon='title', template='base/blocks/h5.html', classname='title')), ('h6', wagtail.wagtailcore.blocks.CharBlock(icon='title', template='base/blocks/h6.html', classname='title')), ('paragraph', wagtail.wagtailcore.blocks.StructBlock((('paragraph', wagtail.wagtailcore.blocks.RichTextBlock()),))), ('image', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock()), ('caption', wagtail.wagtailcore.blocks.TextBlock(required=False)), ('citation', wagtail.wagtailcore.blocks.CharBlock(required=False)), ('alt_text', wagtail.wagtailcore.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock())), label='Image')), ('blockquote', wagtail.wagtailcore.blocks.StructBlock((('quote', wagtail.wagtailcore.blocks.TextBlock('quote title')), ('attribution', wagtail.wagtailcore.blocks.CharBlock()))))), blank=True),
        ),
    ]
