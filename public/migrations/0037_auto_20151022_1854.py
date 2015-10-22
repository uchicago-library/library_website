# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0036_auto_20151022_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donorpage',
            name='page_maintainer',
            field=models.ForeignKey(to='staff.StaffPage', related_name='public_donorpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='locationpage',
            name='page_maintainer',
            field=models.ForeignKey(to='staff.StaffPage', related_name='public_locationpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='standardpage',
            name='page_maintainer',
            field=models.ForeignKey(to='staff.StaffPage', related_name='public_standardpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True),
        ),
    ]
