# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0023_auto_20151204_1927'),
    ]

    operations = [
        migrations.RenameField(
            model_name='donorpage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
        migrations.RenameField(
            model_name='floorplanpage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
        migrations.RenameField(
            model_name='locationpage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
        migrations.RenameField(
            model_name='standardpage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
    ]
