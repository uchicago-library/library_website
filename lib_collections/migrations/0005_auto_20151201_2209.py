# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0004_auto_20151118_2143'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectingareapage',
            name='show_sidebar',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='collectingareapage',
            name='subsection_start',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='collectionpage',
            name='show_sidebar',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='collectionpage',
            name='subsection_start',
            field=models.BooleanField(default=False),
        ),
    ]
