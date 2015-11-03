# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0004_auto_20151020_1954'),
        ('public', '0028_auto_20151021_2103'),
    ]

    operations = [
        migrations.AddField(
            model_name='donorpage',
            name='page_maintainer',
            field=models.ForeignKey(to='staff.StaffPage', null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='public_donorpage_related'),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='page_maintainer',
            field=models.ForeignKey(to='staff.StaffPage', null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='public_locationpage_related'),
        ),
        migrations.AddField(
            model_name='standardpage',
            name='page_maintainer',
            field=models.ForeignKey(to='staff.StaffPage', null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='public_standardpage_related'),
        ),
    ]
