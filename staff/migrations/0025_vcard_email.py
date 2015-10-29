# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0024_auto_20151029_1842'),
    ]

    operations = [
        migrations.AddField(
            model_name='vcard',
            name='email',
            field=models.EmailField(max_length=254, blank=True),
        ),
    ]
