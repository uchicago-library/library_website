# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('intranethome', '0004_auto_20151203_1806'),
    ]

    operations = [
        migrations.RenameField(
            model_name='intranethomepage',
            old_name='subsection_start',
            new_name='start_sidebar_from_here',
        ),
    ]
