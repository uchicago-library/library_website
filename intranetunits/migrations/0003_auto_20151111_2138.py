# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('intranetunits', '0002_auto_20151111_2026'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='intranetunitpagephonenumbers',
            name='page',
        ),
        migrations.DeleteModel(
            name='IntranetUnitPagePhoneNumbers',
        ),
    ]
