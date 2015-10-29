# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0032_auto_20151029_2110'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staffpage',
            name='alphabetize_name_as',
        ),
    ]
