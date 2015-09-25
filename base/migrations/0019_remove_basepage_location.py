# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0018_basepage_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basepage',
            name='location',
        ),
    ]
