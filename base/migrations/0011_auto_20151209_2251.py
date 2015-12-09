# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_auto_20151204_1927'),
    ]

    operations = [
        migrations.RenameField(
            model_name='intranetplainpage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
    ]
