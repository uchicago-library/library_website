# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.blocks
import django.utils.timezone
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, to='wagtailcore.Page', auto_created=True)),
                ('intro', wagtail.wagtailcore.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='NewsPage',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, to='wagtailcore.Page', auto_created=True)),
                ('last_reviewed', models.DateTimeField(verbose_name='Last Reviewed', blank=True, null=True)),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('excerpt', wagtail.wagtailcore.fields.RichTextField(blank=True, null=True)),
                ('body', wagtail.wagtailcore.fields.StreamField((('h2', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), ('paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow'))))),
                ('publish_on', models.DateField(default=django.utils.timezone.now)),
                ('sticky_until', models.DateField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
