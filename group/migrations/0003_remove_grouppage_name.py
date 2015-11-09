# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0002_groupmember_staff'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grouppage',
            name='name',
        ),
    ]
