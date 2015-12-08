# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DirectoryUnit',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('fullName', models.CharField(max_length=1020)),
                ('xmlUrl', models.CharField(max_length=255)),
                ('parentUnit', models.ForeignKey(to='directory_unit.DirectoryUnit')),
            ],
        ),
    ]
