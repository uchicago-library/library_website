# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('intranetunits', '0022_intranetunitpagereports_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intranetunitspage',
            name='unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='intranet_unit_page', to='directory_unit.DirectoryUnit', blank=True),
        ),
    ]
