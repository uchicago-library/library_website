# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0007_remove_staffpage_is_subject_specialist'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffpage',
            name='is_subject_specialist',
            field=models.BooleanField(default=False),
        ),
    ]
