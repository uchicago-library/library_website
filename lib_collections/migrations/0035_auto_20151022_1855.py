# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0034_auto_20151022_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectingareapage',
            name='subject_specialist',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='lib_collections_collectingareapage_subject_specialist'),
        ),
    ]
