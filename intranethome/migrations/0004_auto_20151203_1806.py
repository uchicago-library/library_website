# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('intranethome', '0003_auto_20151202_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intranethomepage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='intranethome_intranethomepage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='intranethomepage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='intranethome_intranethomepage_maintainer', null=True),
        ),
    ]
