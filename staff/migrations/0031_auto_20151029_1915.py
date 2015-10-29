# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0030_auto_20151029_1908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffpage',
            name='cnetid',
            field=models.CharField(default='testcnetid', max_length=255),
            preserve_default=False,
        ),
    ]
