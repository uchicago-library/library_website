# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0022_auto_20151211_2102'),
    ]

    operations = [
        migrations.RenameField(
            model_name='newspage',
            old_name='image',
            new_name='thumbnail',
        ),
    ]
