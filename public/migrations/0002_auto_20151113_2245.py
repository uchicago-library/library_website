# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0000_manual_pre_initial'),
        ('public', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='standardpage',
            name='content_specialist',
            field=models.ForeignKey(to='staff.StaffPage', related_name='public_standardpage_content_specialist', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='standardpage',
            name='editor',
            field=models.ForeignKey(to='staff.StaffPage', related_name='public_standardpage_editor', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='standardpage',
            name='page_maintainer',
            field=models.ForeignKey(to='staff.StaffPage', related_name='public_standardpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
    ]
