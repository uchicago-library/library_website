# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import modelcluster.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0003_add_verbose_names'),
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('staff', '0009_auto_20151218_2147'),
        ('group', '0054_auto_20151211_2102'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupMeetingMinutesPage',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, to='wagtailcore.Page', parent_link=True)),
                ('start_sidebar_from_here', models.BooleanField(default=False)),
                ('show_sidebar', models.BooleanField(default=False)),
                ('last_reviewed', models.DateField(verbose_name='Last Reviewed', null=True, blank=True)),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('editor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='group_groupmeetingminutespage_editor')),
                ('page_maintainer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='group_groupmeetingminutespage_maintainer')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='GroupMeetingMinutesPageTable',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('date', models.DateField()),
                ('summary', models.TextField()),
                ('link', models.URLField(blank=True, default='', max_length=254)),
                ('document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='wagtaildocs.Document', related_name='+')),
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
                ('page_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, to='wagtailcore.Page', parent_link=True)),
                ('start_sidebar_from_here', models.BooleanField(default=False)),
                ('show_sidebar', models.BooleanField(default=False)),
                ('last_reviewed', models.DateField(verbose_name='Last Reviewed', null=True, blank=True)),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('editor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='group_groupreportspage_editor')),
                ('page_maintainer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='group_groupreportspage_maintainer')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='GroupReportsPageTable',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('date', models.DateField()),
                ('summary', models.TextField()),
                ('link', models.URLField(blank=True, default='', max_length=254)),
                ('document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='wagtaildocs.Document', related_name='+')),
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
