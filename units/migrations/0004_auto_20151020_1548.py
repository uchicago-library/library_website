# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('units', '0003_unitpageroleplacement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unitpageroleplacement',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='unit_role_placements', to='units.UnitPage'),
        ),
    ]
