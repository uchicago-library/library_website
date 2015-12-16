# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('intranetunits', '0029_auto_20151216_1440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intranetunitsreportspagetable',
            name='page',
            field=modelcluster.fields.ParentalKey(to='intranetunits.IntranetUnitsReportsPage', related_name='intranet_units_reports'),
        ),
    ]
