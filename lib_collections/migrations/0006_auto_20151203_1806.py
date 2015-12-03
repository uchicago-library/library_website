# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0005_auto_20151201_2209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectingareapage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='lib_collections_collectingareapage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='collectingareapage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='lib_collections_collectingareapage_maintainer', null=True),
        ),
        migrations.AlterField(
            model_name='collectionpage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='lib_collections_collectionpage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='collectionpage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='lib_collections_collectionpage_maintainer', null=True),
        ),
    ]
