# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0040_locationpage_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donorpage',
            name='foobar',
        ),
        migrations.AddField(
            model_name='donorpage',
            name='description',
            field=models.TextField(default='This is a test description'),
            preserve_default=False,
        ),
    ]
