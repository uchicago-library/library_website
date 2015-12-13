# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0007_auto_20151209_2251'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='staffpage',
            options={'ordering': ['title']},
        ),
    ]
