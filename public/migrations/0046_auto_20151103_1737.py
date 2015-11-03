# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0045_standardpage_body'),
    ]

    operations = [
        migrations.RenameField(
            model_name='standardpage',
            old_name='body',
            new_name='body_two',
        ),
    ]
