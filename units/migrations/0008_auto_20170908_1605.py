# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-09-08 21:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0007_auto_20170721_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitpage',
            name='department_head',
            field=models.ForeignKey(blank=True, help_text='Sorts to the top in staff listings.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='department_head_of', to='staff.StaffPage'),
        ),
        migrations.AlterField(
            model_name='unitpage',
            name='department_head_is_interim',
            field=models.BooleanField(default=False, help_text='For HR reports.'),
        ),
        migrations.AlterField(
            model_name='unitpage',
            name='display_in_directory',
            field=models.BooleanField(default=True, help_text="Display this unit in the library's departmental                    directory."),
        ),
        migrations.AlterField(
            model_name='unitpage',
            name='display_in_dropdown',
            field=models.BooleanField(default=False, help_text='Display this unit in the Wagtail admin when a UnitPage                    is selectable in a dropdown menu.'),
        ),
        migrations.AlterField(
            model_name='unitpage',
            name='friendly_name',
            field=models.CharField(blank=True, help_text='e.g.: "Ask a (friendly_name) librarian", or "view all                    (friendly_name) study spaces."', max_length=255),
        ),
        migrations.AlterField(
            model_name='unitpage',
            name='location',
            field=models.ForeignKey(blank=True, help_text='Controls the address, hours and quick numbers that will                    appear on various web pages.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='units_unitpage_related', to='public.LocationPage'),
        ),
        migrations.AlterField(
            model_name='unitpage',
            name='public_web_page',
            field=models.ForeignKey(blank=True, help_text='A link to this page will appear in the departmental                    directory on the library website.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.Page'),
        ),
        migrations.AlterField(
            model_name='unitpage',
            name='room_number',
            field=models.CharField(blank=True, help_text='This will appear in the departmental directory on the                    library website.', max_length=32),
        ),
    ]