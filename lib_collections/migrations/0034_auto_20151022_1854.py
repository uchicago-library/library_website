# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0033_auto_20151022_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectingareapage',
            name='page_maintainer',
            field=models.ForeignKey(to='staff.StaffPage', related_name='lib_collections_collectingareapage_maintainer', on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='collectionpage',
            name='page_maintainer',
            field=models.ForeignKey(to='staff.StaffPage', related_name='lib_collections_collectionpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True),
        ),
    ]
