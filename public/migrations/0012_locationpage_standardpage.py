# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.blocks
import wagtail.wagtailimages.blocks
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0001_squashed_0016_change_page_url_path_to_text_field'),
        ('public', '0011_auto_20150925_1548'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationPage',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, auto_created=True, to='wagtailcore.Page', parent_link=True, primary_key=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('last_reviewed', models.DateTimeField(null=True, blank=True, verbose_name='Last Reviewed')),
                ('name', models.CharField(max_length=45)),
                ('is_building', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='StandardPage',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, auto_created=True, to='wagtailcore.Page', parent_link=True, primary_key=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('last_reviewed', models.DateTimeField(null=True, blank=True, verbose_name='Last Reviewed')),
                ('body', wagtail.wagtailcore.fields.StreamField((('heading', wagtail.wagtailcore.blocks.CharBlock(classname='full title', icon='title')), ('paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow')), ('image', wagtail.wagtailimages.blocks.ImageChooserBlock(icon='image / picture'))))),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
