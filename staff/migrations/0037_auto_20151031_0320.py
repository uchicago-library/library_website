# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0036_grouppageplacement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppageplacement',
            name='group_or_committee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='group.GroupPage', related_name='group_page', null=True),
        ),
        migrations.AlterField(
            model_name='staffpage',
            name='supervisor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='staff.StaffPage', null=True),
        ),
    ]
