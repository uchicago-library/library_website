# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields
import wagtail.wagtailcore.blocks
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0019_verbose_names_cleanup'),
    ]

    operations = [
        migrations.CreateModel(
            name='DonorPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('last_reviewed', models.DateTimeField(null=True, verbose_name=b'Last Reviewed', blank=True)),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='LocationPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('last_reviewed', models.DateTimeField(null=True, verbose_name=b'Last Reviewed', blank=True)),
                ('address_1', models.CharField(max_length=255, blank=True)),
                ('address_2', models.CharField(max_length=255, blank=True)),
                ('city', models.CharField(max_length=255, blank=True)),
                ('country', models.CharField(max_length=255, blank=True)),
                ('postal_code', models.CharField(blank=True, max_length=5, validators=[django.core.validators.RegexValidator(regex=b'^[0-9]{5}$', message=b'Please enter the postal code as a five digit number, e.g. 60637')])),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('phone_label', models.CharField(max_length=25, blank=True)),
                ('phone_number', models.CharField(blank=True, max_length=12, validators=[django.core.validators.RegexValidator(regex=b'^[0-9]{3}-[0-9]{3}-[0-9]{4}$', message=b'Please enter the phone number using the format 773-123-4567')])),
                ('description', models.TextField()),
                ('library_floorplan_link', models.URLField(default=b'', blank=True)),
                ('libcal_library_id', models.IntegerField(null=True, blank=True)),
                ('google_map_link', models.URLField(default=b'', blank=True)),
                ('reservation_url', models.URLField(default=b'', blank=True)),
                ('reservation_display_text', models.CharField(max_length=45, blank=True)),
                ('is_building', models.BooleanField(default=False)),
                ('is_phone_zone', models.BooleanField(default=False)),
                ('is_collaboration_zone', models.BooleanField(default=False)),
                ('is_meal_zone', models.BooleanField(default=False)),
                ('is_quiet_zone', models.BooleanField(default=False)),
                ('is_study_space', models.BooleanField(default=False)),
                ('is_teaching_space', models.BooleanField(default=False)),
                ('is_event_space', models.BooleanField(default=False)),
                ('is_24_hours', models.BooleanField(default=False)),
                ('is_reservable', models.BooleanField(default=False)),
                ('has_carrels', models.BooleanField(default=False)),
                ('has_board', models.BooleanField(default=False)),
                ('has_printing', models.BooleanField(default=False)),
                ('has_soft_seating', models.BooleanField(default=False)),
                ('has_cps', models.BooleanField(default=False)),
                ('has_dual_monitors', models.BooleanField(default=False)),
                ('has_single_tables', models.BooleanField(default=False)),
                ('has_large_tables', models.BooleanField(default=False)),
                ('has_screen', models.BooleanField(default=False)),
                ('has_natural_light', models.BooleanField(default=False)),
                ('is_no_food_allowed', models.BooleanField(default=False)),
                ('has_book_scanner', models.BooleanField(default=False)),
                ('has_public_computer', models.BooleanField(default=False)),
                ('is_snacks_allowed', models.BooleanField(default=False)),
                ('has_standing_desk', models.BooleanField(default=False)),
                ('has_lockers', models.BooleanField(default=False)),
                ('has_day_lockers', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
        migrations.CreateModel(
            name='LocationPageDonorPlacement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StandardPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('last_reviewed', models.DateTimeField(null=True, verbose_name=b'Last Reviewed', blank=True)),
                ('body', wagtail.wagtailcore.fields.StreamField([(b'h2', wagtail.wagtailcore.blocks.CharBlock(classname=b'title', icon=b'title')), (b'h3', wagtail.wagtailcore.blocks.CharBlock(classname=b'title', icon=b'title')), (b'h4', wagtail.wagtailcore.blocks.CharBlock(classname=b'title', icon=b'title')), (b'paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon=b'pilcrow'))])),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
