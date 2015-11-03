# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0003_auto_20151008_1409'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupmember',
            name='group',
        ),
        migrations.RemoveField(
            model_name='groupmember',
            name='staff',
        ),
        migrations.RemoveField(
            model_name='grouppage',
            name='email',
        ),
        migrations.RemoveField(
            model_name='grouppage',
            name='intro',
        ),
        migrations.RemoveField(
            model_name='grouppage',
            name='name',
        ),
        migrations.AddField(
            model_name='grouppage',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.DeleteModel(
            name='GroupMember',
        ),
    ]
