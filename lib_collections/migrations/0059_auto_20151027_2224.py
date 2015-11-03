# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0058_auto_20151027_2217'),
    ]

    operations = [
        migrations.RenameField(
            model_name='collectingareapage',
            old_name='link_text',
            new_name='guide_link_text',
        ),
        migrations.RenameField(
            model_name='collectingareapage',
            old_name='link_url',
            new_name='guide_link_url',
        ),
    ]
