# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('staff', '0000_manual_pre_initial'),
        ('group', '0059_auto_20160107_1931'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupMeetingMinutesIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, serialize=False, to='wagtailcore.Page', on_delete=models.CASCADE)),
                ('start_sidebar_from_here', models.BooleanField(default=False)),
                ('show_sidebar', models.BooleanField(default=False)),
                ('last_reviewed', models.DateField(null=True, verbose_name='Last Reviewed', blank=True)),
                ('sort_order', models.IntegerField(default=0, blank=True)),
                ('editor', models.ForeignKey(related_name='group_groupmeetingminutesindexpage_editor', blank=True, null=True, to='staff.StaffPage', on_delete=django.db.models.deletion.SET_NULL)),
                ('page_maintainer', models.ForeignKey(related_name='group_groupmeetingminutesindexpage_maintainer', blank=True, null=True, to='staff.StaffPage', on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
