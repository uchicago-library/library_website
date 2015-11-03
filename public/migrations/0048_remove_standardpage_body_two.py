# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0047_standardpage_body'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='standardpage',
            name='body_two',
        ),
    ]
