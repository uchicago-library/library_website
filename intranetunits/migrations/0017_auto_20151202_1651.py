# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0000_manual_pre_initial'),
        ('intranetunits', '0016_auto_20151201_2209'),
    ]

    operations = [
        migrations.AddField(
            model_name='intranetunitsindexpage',
            name='editor',
            field=models.ForeignKey(null=True, to='staff.StaffPage', related_name='intranetunits_intranetunitsindexpage_editor', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='intranetunitsindexpage',
            name='last_reviewed',
            field=models.DateField(verbose_name='Last Reviewed', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='intranetunitsindexpage',
            name='page_maintainer',
            field=models.ForeignKey(null=True, to='staff.StaffPage', related_name='intranetunits_intranetunitsindexpage_maintainer', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='intranetunitsindexpage',
            name='show_sidebar',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='intranetunitsindexpage',
            name='sort_order',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='intranetunitsindexpage',
            name='subsection_start',
            field=models.BooleanField(default=False),
        ),
    ]
