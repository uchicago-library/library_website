# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0039_auto_20151029_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationpage',
            name='description',
            field=models.TextField(default='This is a test description'),
            preserve_default=False,
        ),
    ]
