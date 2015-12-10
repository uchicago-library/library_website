# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0007_auto_20151209_2251'),
        ('directory_unit', '0002_auto_20151208_1739'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnitSupervisor',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('supervisor', models.ForeignKey(to='staff.StaffPage', on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('unit', models.ForeignKey(null=True, to='directory_unit.DirectoryUnit')),
            ],
        ),
    ]
