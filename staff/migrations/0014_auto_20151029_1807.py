# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0013_auto_20151029_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vcard',
            name='faculty_exchange',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
