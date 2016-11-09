# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('staff', '0000_manual_pre_initial'),
        ('group', '0060_groupmeetingminutesindexpage'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupReportsIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, to='wagtailcore.Page', serialize=False, parent_link=True, primary_key=True)),
                ('start_sidebar_from_here', models.BooleanField(default=False)),
                ('show_sidebar', models.BooleanField(default=False)),
                ('last_reviewed', models.DateField(blank=True, verbose_name='Last Reviewed', null=True)),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('editor', models.ForeignKey(to='staff.StaffPage', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, related_name='group_groupreportsindexpage_editor')),
                ('page_maintainer', models.ForeignKey(to='staff.StaffPage', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, related_name='group_groupreportsindexpage_maintainer')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
