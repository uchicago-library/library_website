# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0020_locationpage_libcal_library_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationpage',
            name='google_map_link',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='reservatuion_link_display_text',
            field=models.CharField(blank=True, max_length=45),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='room_reservation_link',
            field=models.URLField(blank=True, default=''),
        ),
    ]
