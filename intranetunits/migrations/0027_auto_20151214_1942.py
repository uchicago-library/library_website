# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('intranetunits', '0026_auto_20151211_2102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intranetunitpagereports',
            name='link',
            field=models.URLField(blank=True, default='', max_length=254),
        ),
    ]
