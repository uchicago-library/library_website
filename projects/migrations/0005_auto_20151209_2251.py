# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_auto_20151203_1806'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectindexpage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
        migrations.RenameField(
            model_name='projectpage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
    ]
