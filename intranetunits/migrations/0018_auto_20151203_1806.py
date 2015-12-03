# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('intranetunits', '0017_auto_20151202_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intranetunitsindexpage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='intranetunits_intranetunitsindexpage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='intranetunitsindexpage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='intranetunits_intranetunitsindexpage_maintainer', null=True),
        ),
        migrations.AlterField(
            model_name='intranetunitspage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='intranetunits_intranetunitspage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='intranetunitspage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='intranetunits_intranetunitspage_maintainer', null=True),
        ),
    ]
