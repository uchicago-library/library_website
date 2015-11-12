# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailsearch.index
import modelcluster.fields
import wagtail.wagtailcore.fields
import django.db.models.deletion
import wagtail.wagtailcore.blocks
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0002_auto_20151111_2026'),
        ('wagtailcore', '0019_verbose_names_cleanup'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=255)),
            ],
            bases=(models.Model, wagtail.wagtailsearch.index.Indexed),
        ),
        migrations.CreateModel(
            name='UnitPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('last_reviewed', models.DateTimeField(null=True, verbose_name=b'Last Reviewed', blank=True)),
                ('fax_number', models.CharField(blank=True, max_length=12, validators=[django.core.validators.RegexValidator(regex=b'^[0-9]{3}-[0-9]{3}-[0-9]{4}$', message=b'Please enter the phone number using the format 773-123-4567')])),
                ('display_in_directory', models.BooleanField(default=False)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('contact_url', models.URLField(default=b'', blank=True)),
                ('room_number', models.CharField(max_length=32, blank=True)),
                ('is_hub_page', models.BooleanField(default=False)),
                ('body', wagtail.wagtailcore.fields.StreamField([(b'h2', wagtail.wagtailcore.blocks.CharBlock(classname=b'title', icon=b'title')), (b'h3', wagtail.wagtailcore.blocks.CharBlock(classname=b'title', icon=b'title')), (b'h4', wagtail.wagtailcore.blocks.CharBlock(classname=b'title', icon=b'title')), (b'paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon=b'pilcrow'))])),
                ('editor', models.ForeignKey(related_name='units_unitpage_editor', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True)),
                ('location', models.ForeignKey(related_name='units_unitpage_related', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='public.LocationPage', null=True)),
                ('page_maintainer', models.ForeignKey(related_name='units_unitpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True)),
                ('public_web_page', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtailcore.Page', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
        migrations.CreateModel(
            name='UnitPagePhoneNumbers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('phone_label', models.CharField(max_length=25, blank=True)),
                ('phone_number', models.CharField(blank=True, max_length=12, validators=[django.core.validators.RegexValidator(regex=b'^[0-9]{3}-[0-9]{3}-[0-9]{4}$', message=b'Please enter the phone number using the format 773-123-4567')])),
                ('page', modelcluster.fields.ParentalKey(related_name='phone_numbers', to='units.UnitPage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UnitPageReports',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('date', models.DateField()),
                ('summary', models.TextField()),
                ('link', models.URLField(default=b'', max_length=254)),
                ('page', modelcluster.fields.ParentalKey(related_name='unit_reports', to='units.UnitPage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UnitPageRolePlacement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('page', modelcluster.fields.ParentalKey(related_name='unit_role_placements', to='units.UnitPage')),
                ('role', models.ForeignKey(related_name='+', to='units.Role')),
            ],
            options={
                'verbose_name': 'Unit Placement',
                'verbose_name_plural': 'Unit Placements',
            },
        ),
    ]
