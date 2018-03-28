# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.core.blocks
import modelcluster.fields
import django.utils.timezone
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, to='wagtailcore.Page', auto_created=True, on_delete=models.CASCADE)),
                ('intro', wagtail.core.fields.RichTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='GroupMembers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Member',
                'verbose_name_plural': 'Members',
            },
        ),
        migrations.CreateModel(
            name='GroupPage',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, to='wagtailcore.Page', auto_created=True, on_delete=models.CASCADE)),
                ('last_reviewed', models.DateTimeField(verbose_name='Last Reviewed', blank=True, null=True)),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('meeting_location', models.CharField(max_length=255, blank=True)),
                ('meeting_time', models.TimeField(blank=True, default=django.utils.timezone.now)),
                ('meeting_frequency', models.CharField(max_length=255, blank=True)),
                ('intro', wagtail.core.fields.RichTextField()),
                ('is_active', models.BooleanField(default=False)),
                ('body', wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow'))))),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
        migrations.CreateModel(
            name='GroupPageMeetingMinutes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('date', models.DateField()),
                ('summary', models.TextField()),
                ('link', models.URLField(max_length=254, default='')),
                ('page', modelcluster.fields.ParentalKey(related_name='meeting_minutes', to='group.GroupPage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GroupPageReports',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('date', models.DateField()),
                ('summary', models.TextField()),
                ('link', models.URLField(max_length=254, default='')),
                ('page', modelcluster.fields.ParentalKey(related_name='group_reports', to='group.GroupPage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
