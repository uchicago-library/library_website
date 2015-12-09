# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('intranetunits', '0023_auto_20151208_2206'),
    ]

    operations = [
        migrations.RenameField(
            model_name='intranetunitsindexpage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
        migrations.RenameField(
            model_name='intranetunitspage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
    ]
