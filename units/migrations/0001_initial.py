# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailcore.blocks
import wagtail.wagtailsearch.index
import django.db.models.deletion
import django.core.validators
import modelcluster.fields
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0002_auto_20151113_2245'),
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('text', models.CharField(max_length=255)),
            ],
            bases=(models.Model, wagtail.wagtailsearch.index.Indexed),
        ),
        migrations.CreateModel(
            name='UnitPage',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, to='wagtailcore.Page', auto_created=True)),
                ('last_reviewed', models.DateTimeField(verbose_name='Last Reviewed', blank=True, null=True)),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('fax_number', models.CharField(validators=[django.core.validators.RegexValidator(regex='^[0-9]{3}-[0-9]{3}-[0-9]{4}$', message='Please enter the phone number using the format 773-123-4567')], max_length=12, blank=True)),
                ('display_in_directory', models.BooleanField(default=False)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('contact_url', models.URLField(default='', blank=True)),
                ('room_number', models.CharField(max_length=32, blank=True)),
                ('is_hub_page', models.BooleanField(default=False)),
                ('body', wagtail.wagtailcore.fields.StreamField((('h2', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.wagtailcore.blocks.CharBlock(classname='title', icon='title')), ('paragraph', wagtail.wagtailcore.blocks.RichTextBlock(icon='pilcrow'))))),
                ('editor', models.ForeignKey(to='staff.StaffPage', related_name='units_unitpage_editor', on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('location', models.ForeignKey(to='public.LocationPage', on_delete=django.db.models.deletion.SET_NULL, related_name='units_unitpage_related', blank=True, null=True)),
                ('page_maintainer', models.ForeignKey(to='staff.StaffPage', related_name='units_unitpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('public_web_page', models.ForeignKey(to='wagtailcore.Page', on_delete=django.db.models.deletion.SET_NULL, related_name='+', blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
        migrations.CreateModel(
            name='UnitPagePhoneNumbers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('phone_label', models.CharField(max_length=25, blank=True)),
                ('phone_number', models.CharField(validators=[django.core.validators.RegexValidator(regex='^[0-9]{3}-[0-9]{3}-[0-9]{4}$', message='Please enter the phone number using the format 773-123-4567')], max_length=12, blank=True)),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('date', models.DateField()),
                ('summary', models.TextField()),
                ('link', models.URLField(max_length=254, default='')),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('page', modelcluster.fields.ParentalKey(related_name='unit_role_placements', to='units.UnitPage')),
                ('role', models.ForeignKey(related_name='+', to='units.Role')),
            ],
            options={
                'verbose_name': 'Unit Placement',
                'verbose_name_plural': 'Unit Placements',
            },
        ),
    ]
