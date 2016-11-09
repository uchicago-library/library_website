# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0003_add_verbose_names'),
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('staff', '0000_manual_pre_initial'),
        ('intranetunits', '0026_auto_20151211_2102'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntranetUnitsReportsPage',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, to='wagtailcore.Page', parent_link=True)),
                ('start_sidebar_from_here', models.BooleanField(default=False)),
                ('show_sidebar', models.BooleanField(default=False)),
                ('last_reviewed', models.DateField(verbose_name='Last Reviewed', null=True, blank=True)),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('editor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='intranetunits_intranetunitsreportspage_editor')),
                ('page_maintainer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='intranetunits_intranetunitsreportspage_maintainer')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='IntranetUnitsReportsPageTable',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('date', models.DateField()),
                ('summary', models.TextField()),
                ('link', models.URLField(blank=True, default='', max_length=254)),
                ('document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='wagtaildocs.Document', related_name='+')),
                ('page', modelcluster.fields.ParentalKey(to='intranetunits.IntranetUnitsReportsPage', related_name='intranet_units_reports')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
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
