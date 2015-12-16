# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import modelcluster.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0008_auto_20151213_2022'),
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('wagtaildocs', '0003_add_verbose_names'),
        ('intranetunits', '0027_auto_20151214_1942'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntranetUnitReportsPageTable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, blank=True, editable=False)),
                ('date', models.DateField()),
                ('summary', models.TextField()),
                ('link', models.URLField(max_length=254, blank=True, default='')),
                ('document', models.ForeignKey(null=True, blank=True, to='wagtaildocs.Document', on_delete=django.db.models.deletion.SET_NULL, related_name='+')),
                ('page', modelcluster.fields.ParentalKey(related_name='intranet_unit_reports', to='intranetunits.IntranetUnitsPage')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
        migrations.CreateModel(
            name='IntranetUnitsReportsPage',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, primary_key=True, to='wagtailcore.Page', parent_link=True, auto_created=True)),
                ('start_sidebar_from_here', models.BooleanField(default=False)),
                ('show_sidebar', models.BooleanField(default=False)),
                ('last_reviewed', models.DateField(null=True, verbose_name='Last Reviewed', blank=True)),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('editor', models.ForeignKey(null=True, blank=True, to='staff.StaffPage', on_delete=django.db.models.deletion.SET_NULL, related_name='intranetunits_intranetunitsreportspage_editor')),
                ('page_maintainer', models.ForeignKey(null=True, blank=True, to='staff.StaffPage', on_delete=django.db.models.deletion.SET_NULL, related_name='intranetunits_intranetunitsreportspage_maintainer')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.RemoveField(
            model_name='intranetunitpagereports',
            name='document',
        ),
        migrations.RemoveField(
            model_name='intranetunitpagereports',
            name='page',
        ),
        migrations.DeleteModel(
            name='IntranetUnitPageReports',
        ),
    ]
