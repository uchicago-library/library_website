# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0006_auto_20151203_1806'),
    ]

    operations = [
        migrations.RenameField(
            model_name='collectingareapage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
        migrations.RenameField(
            model_name='collectionpage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
    ]
