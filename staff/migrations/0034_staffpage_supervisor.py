# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0033_remove_staffpage_alphabetize_name_as'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffpage',
            name='supervisor',
            field=models.ForeignKey(to='staff.StaffPage', null=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
