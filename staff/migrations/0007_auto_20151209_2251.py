# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0006_auto_20151208_2124'),
    ]

    operations = [
        migrations.RenameField(
            model_name='staffindexpage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
        migrations.RenameField(
            model_name='staffpage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
    ]
