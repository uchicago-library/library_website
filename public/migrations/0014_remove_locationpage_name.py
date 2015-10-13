# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0013_auto_20150925_1550'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='locationpage',
            name='name',
        ),
    ]
