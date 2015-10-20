# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0021_auto_20151001_1622'),
    ]

    operations = [
        migrations.RenameField(
            model_name='locationpage',
            old_name='reservatuion_link_display_text',
            new_name='reservation_display_text',
        ),
        migrations.RenameField(
            model_name='locationpage',
            old_name='room_reservation_link',
            new_name='reservation_url',
        ),
    ]
