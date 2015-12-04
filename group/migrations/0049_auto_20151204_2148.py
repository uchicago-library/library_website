# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0048_auto_20151204_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupmembers',
            name='role',
            field=models.ForeignKey(null=True, to='group.GroupMemberRole', related_name='+', blank=True),
        ),
    ]
