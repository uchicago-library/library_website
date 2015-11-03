# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields
import wagtail.wagtailimages.blocks
import django.db.models.deletion
import wagtail.wagtailcore.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0008_image_created_at_index'),
        ('wagtailcore', '0019_verbose_names_cleanup'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('description', models.TextField(blank=True)),
                ('last_reviewed', models.DateTimeField(null=True, verbose_name=b'Last Reviewed', blank=True)),
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
                ('location', models.ForeignKey(related_name='public_locationpage_related', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='public.LocationPage', null=True)),
                ('location_photo', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtailimages.Image', null=True)),
                ('parent_building', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='public.LocationPage', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='StandardPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('description', models.TextField(blank=True)),
                ('last_reviewed', models.DateTimeField(null=True, verbose_name=b'Last Reviewed', blank=True)),
                ('body', wagtail.wagtailcore.fields.StreamField([(b'heading', wagtail.wagtailcore.blocks.CharBlock(classname=b'full title', icon=b'title')), (b'paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon=b'pilcrow')), (b'image', wagtail.wagtailimages.blocks.ImageChooserBlock(icon=b'image / picture'))])),
                ('location', models.ForeignKey(related_name='public_standardpage_related', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='public.LocationPage', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
