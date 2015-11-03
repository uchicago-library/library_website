# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0001_initial'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupmember',
            name='staff',
            field=models.ForeignKey(to='staff.StaffPage'),
        ),
    ]
