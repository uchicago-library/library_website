# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields
import wagtail.wagtailcore.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newspage',
            name='body',
            field=wagtail.wagtailcore.fields.StreamField((('h2', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title')), ('h3', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title')), ('h4', wagtail.wagtailcore.blocks.CharBlock(icon='title', classname='title')), ('paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow')))),
        ),
    ]
