# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0052_grouppagereports_document'),
    ]

    operations = [
        migrations.RenameField(
            model_name='groupindexpage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
        migrations.RenameField(
            model_name='grouppage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
    ]
