# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),
        ('intranetunits', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='intranetunitspage',
            name='editor',
            field=models.ForeignKey(related_name='intranetunits_intranetunitspage_editor', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='intranetunitspage',
            name='page_maintainer',
            field=models.ForeignKey(related_name='intranetunits_intranetunitspage_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='intranetunitpagereports',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='intranet_unit_reports', to='intranetunits.IntranetUnitsPage'),
        ),
        migrations.AddField(
            model_name='intranetunitpagephonenumbers',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='intranet_phone_numbers', to='intranetunits.IntranetUnitsPage'),
        ),
    ]
