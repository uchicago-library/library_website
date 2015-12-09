# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0022_unitpagereports_document'),
    ]

    operations = [
        migrations.RenameField(
            model_name='unitindexpage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
        migrations.RenameField(
            model_name='unitpage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
    ]
