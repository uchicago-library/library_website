# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0046_auto_20151204_1927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupmembers',
            name='role',
            field=models.ForeignKey(to='group.GroupMemberRole', null=True, default='', related_name='+', blank=True),
        ),
    ]
