# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory_unit', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directoryunit',
            name='fullName',
            field=models.CharField(default='', max_length=1020),
        ),
        migrations.AlterField(
            model_name='directoryunit',
            name='parentUnit',
            field=models.ForeignKey(null=True, to='directory_unit.DirectoryUnit'),
        ),
    ]
