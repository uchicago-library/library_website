# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0043_locationpagedonorplacement'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='standardpage',
            name='body',
        ),
    ]
