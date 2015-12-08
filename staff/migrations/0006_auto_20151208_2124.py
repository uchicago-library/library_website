# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0005_auto_20151203_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vcard',
            name='unit',
            field=models.ForeignKey(null=True, related_name='staff_vcard_related', on_delete=django.db.models.deletion.SET_NULL, to='directory_unit.DirectoryUnit', blank=True),
        ),
    ]
