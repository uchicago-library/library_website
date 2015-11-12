# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('intranetunits', '0004_auto_20151111_2142'),
    ]

    operations = [
        migrations.AddField(
            model_name='intranetunitspage',
            name='sort_order',
            field=models.IntegerField(default=0, blank=True),
        ),
    ]
