# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('staff', '0000_manual_pre_initial'),
        ('intranetunits', '0030_auto_20160107_1931'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntranetUnitsReportsIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, to='wagtailcore.Page', serialize=False, primary_key=True, auto_created=True, on_delete=models.CASCADE)),
                ('start_sidebar_from_here', models.BooleanField(default=False)),
                ('show_sidebar', models.BooleanField(default=False)),
                ('last_reviewed', models.DateField(verbose_name='Last Reviewed', blank=True, null=True)),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('editor', models.ForeignKey(blank=True, related_name='intranetunits_intranetunitsreportsindexpage_editor', to='staff.StaffPage', on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('page_maintainer', models.ForeignKey(blank=True, related_name='intranetunits_intranetunitsreportsindexpage_maintainer', to='staff.StaffPage', on_delete=django.db.models.deletion.SET_NULL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
