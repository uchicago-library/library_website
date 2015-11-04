# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0012_groupmembers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='groupmembers',
            old_name='staff_members',
            new_name='group_member',
        ),
    ]
