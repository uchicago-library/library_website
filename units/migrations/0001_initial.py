# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.core.blocks
import wagtail.search.index
import django.db.models.deletion
import django.core.validators
import modelcluster.fields
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0000_manual_pre_initial'),
        ('public', '0002_auto_20151113_2245'),
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('staff', '0000_manual_pre_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('text', models.CharField(max_length=255)),
            ],
            bases=(models.Model, wagtail.search.index.Indexed),
        ),
        migrations.AddField(
            model_name='unitpage',
            name='last_reviewed',
            field=models.DateTimeField(verbose_name='Last Reviewed', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='unitpage',
            name='sort_order',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='unitpage',
            name='fax_number',
            field=models.CharField(validators=[django.core.validators.RegexValidator(regex='^[0-9]{3}-[0-9]{3}-[0-9]{4}$', message='Please enter the phone number using the format 773-123-4567')], max_length=12, blank=True),
        ),
        migrations.AddField(
            model_name='unitpage',
            name='display_in_directory',
            field=models.BooleanField(default=False)
        ),
        migrations.AddField(
            model_name='unitpage',
            name='email',
            field=models.EmailField(max_length=254, blank=True),
        ),
        migrations.AddField(
            model_name='unitpage',
            name='contact_url',
            field=models.URLField(default='', blank=True),
        ),
        migrations.AddField(
            model_name='unitpage',
            name='room_number',
            field=models.CharField(max_length=32, blank=True),
        ),
        migrations.AddField(
            model_name='unitpage',
            name='is_hub_page',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='unitpage',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title')), ('paragraph', wagtail.core.blocks.RichTextBlock(icon='pilcrow')))),
        ),
        migrations.AddField(
            model_name='unitpage',
            name='editor',
            field=models.ForeignKey(to='staff.StaffPage', related_name='units_unitpage_editor', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='unitpage',
            name='location',
            field=models.ForeignKey(to='public.LocationPage', on_delete=django.db.models.deletion.SET_NULL, related_name='units_unitpage_related', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='unitpage',
            name='page_maintainer',
            field=models.ForeignKey(to='staff.StaffPage', related_name='units_unitpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='unitpage',
            name='public_web_page',
            field=models.ForeignKey(to='wagtailcore.Page', on_delete=django.db.models.deletion.SET_NULL, related_name='+', blank=True, null=True),
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
                ('role', models.ForeignKey(related_name='+', to='units.Role', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Unit Placement',
                'verbose_name_plural': 'Unit Placements',
            },
        ),
    ]
