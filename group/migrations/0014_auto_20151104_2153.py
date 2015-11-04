# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0013_auto_20151104_2146'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='groupmembers',
            options={'verbose_name': 'Member', 'verbose_name_plural': 'Group Members'},
        ),
    ]
