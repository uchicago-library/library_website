# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.core.fields
import wagtail.core.blocks
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0000_manual_pre_initial'),
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='TOCPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', primary_key=True, auto_created=True, serialize=False, parent_link=True, on_delete=models.CASCADE)),
                ('start_sidebar_from_here', models.BooleanField(default=False)),
                ('show_sidebar', models.BooleanField(default=False)),
                ('last_reviewed', models.DateField(verbose_name='Last Reviewed', null=True, blank=True)),
                ('sort_order', models.IntegerField(default=0, blank=True)),
                ('body', wagtail.core.fields.StreamField((('list_block', wagtail.core.blocks.StructBlock((('icon', wagtail.core.blocks.CharBlock(help_text='Add a Font Awesome icon name here')), ('heading', wagtail.core.blocks.CharBlock()), ('text', wagtail.core.blocks.RichTextBlock())))),))),
                ('editor', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', blank=True, related_name='intranettocs_tocpage_editor', null=True)),
                ('page_maintainer', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', blank=True, related_name='intranettocs_tocpage_maintainer', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
