# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('intranetunits', '0028_auto_20151228_2126'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='intranetunitsreportspagetable',
            name='document',
        ),
        migrations.RemoveField(
            model_name='intranetunitsreportspagetable',
            name='link',
        ),
    ]
