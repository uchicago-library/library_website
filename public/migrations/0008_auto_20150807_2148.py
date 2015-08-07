# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields
import wagtail.wagtailimages.blocks
import wagtail.wagtailcore.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0007_auto_20150807_2133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standardpage',
            name='body',
            field=wagtail.wagtailcore.fields.StreamField((('heading', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='full title')), ('paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow')), ('image', wagtail.wagtailimages.blocks.ImageChooserBlock(icon='image / picture')))),
        ),
    ]
