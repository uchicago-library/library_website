# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory_unit', '0003_unitsupervisor'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='directoryunit',
            options={'ordering': ['fullName']},
        ),
    ]
