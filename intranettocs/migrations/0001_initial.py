# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.fields
import wagtail.wagtailcore.blocks
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0007_auto_20151209_2251'),
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='TOCPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', primary_key=True, auto_created=True, serialize=False, parent_link=True)),
                ('start_sidebar_from_here', models.BooleanField(default=False)),
                ('show_sidebar', models.BooleanField(default=False)),
                ('last_reviewed', models.DateField(verbose_name='Last Reviewed', null=True, blank=True)),
                ('sort_order', models.IntegerField(default=0, blank=True)),
                ('body', wagtail.wagtailcore.fields.StreamField((('list_block', wagtail.wagtailcore.blocks.StructBlock((('icon', wagtail.wagtailcore.blocks.CharBlock(help_text='Add a Font Awesome icon name here')), ('heading', wagtail.wagtailcore.blocks.CharBlock()), ('text', wagtail.wagtailcore.blocks.RichTextBlock())))),))),
                ('editor', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', blank=True, related_name='intranettocs_tocpage_editor', null=True)),
                ('page_maintainer', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', blank=True, related_name='intranettocs_tocpage_maintainer', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
