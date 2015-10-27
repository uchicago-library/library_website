# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0057_auto_20151027_1902'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectingareapage',
            name='link_text',
            field=models.CharField(max_length=255, default=''),
        ),
        migrations.AddField(
            model_name='collectingareapage',
            name='link_url',
            field=models.URLField(verbose_name='Libguide URL', default=''),
        ),
    ]
