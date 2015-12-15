# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0003_add_verbose_names'),
        ('staff', '0008_auto_20151213_2022'),
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('group', '0054_auto_20151211_2102'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupMeetingMinutesPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', serialize=False, auto_created=True, primary_key=True, parent_link=True)),
                ('start_sidebar_from_here', models.BooleanField(default=False)),
                ('show_sidebar', models.BooleanField(default=False)),
                ('last_reviewed', models.DateField(blank=True, null=True, verbose_name='Last Reviewed')),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('editor', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='staff.StaffPage', blank=True, related_name='group_groupmeetingminutespage_editor')),
                ('page_maintainer', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='staff.StaffPage', blank=True, related_name='group_groupmeetingminutespage_maintainer')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='GroupMeetingMinutesPageTable',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('date', models.DateField()),
                ('summary', models.TextField()),
                ('link', models.URLField(blank=True, default='', max_length=254)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='wagtaildocs.Document', blank=True, related_name='+')),
                ('page', modelcluster.fields.ParentalKey(to='group.GroupMeetingMinutesPage', related_name='meeting_minutes')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
        migrations.CreateModel(
            name='GroupReportsPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', serialize=False, auto_created=True, primary_key=True, parent_link=True)),
                ('start_sidebar_from_here', models.BooleanField(default=False)),
                ('show_sidebar', models.BooleanField(default=False)),
                ('last_reviewed', models.DateField(blank=True, null=True, verbose_name='Last Reviewed')),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('editor', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='staff.StaffPage', blank=True, related_name='group_groupreportspage_editor')),
                ('page_maintainer', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='staff.StaffPage', blank=True, related_name='group_groupreportspage_maintainer')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='GroupReportsPageTable',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('date', models.DateField()),
                ('summary', models.TextField()),
                ('link', models.URLField(blank=True, default='', max_length=254)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='wagtaildocs.Document', blank=True, related_name='+')),
                ('page', modelcluster.fields.ParentalKey(to='group.GroupReportsPage', related_name='group_reports')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
        migrations.RemoveField(
            model_name='grouppagemeetingminutes',
            name='document',
        ),
        migrations.RemoveField(
            model_name='grouppagemeetingminutes',
            name='page',
        ),
        migrations.RemoveField(
            model_name='grouppagereports',
            name='document',
        ),
        migrations.RemoveField(
            model_name='grouppagereports',
            name='page',
        ),
        migrations.DeleteModel(
            name='GroupPageMeetingMinutes',
        ),
        migrations.DeleteModel(
            name='GroupPageReports',
        ),
    ]
