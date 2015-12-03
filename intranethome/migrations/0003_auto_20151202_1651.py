# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0004_auto_20151202_1651'),
        ('intranethome', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='intranethomepage',
            name='editor',
            field=models.ForeignKey(null=True, to='staff.StaffPage', related_name='intranethome_intranethomepage_editor', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='intranethomepage',
            name='last_reviewed',
            field=models.DateField(verbose_name='Last Reviewed', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='intranethomepage',
            name='page_maintainer',
            field=models.ForeignKey(null=True, to='staff.StaffPage', related_name='intranethome_intranethomepage_maintainer', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='intranethomepage',
            name='show_sidebar',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='intranethomepage',
            name='sort_order',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='intranethomepage',
            name='subsection_start',
            field=models.BooleanField(default=False),
        ),
    ]
