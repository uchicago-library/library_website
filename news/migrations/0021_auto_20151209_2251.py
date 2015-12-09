# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0020_auto_20151204_1927'),
    ]

    operations = [
        migrations.RenameField(
            model_name='newsindexpage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
        migrations.RenameField(
            model_name='newspage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
    ]
