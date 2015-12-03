# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0020_auto_20151201_2209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donorpage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='public_donorpage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='donorpage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='public_donorpage_maintainer', null=True),
        ),
        migrations.AlterField(
            model_name='floorplanpage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='public_floorplanpage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='floorplanpage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='public_floorplanpage_maintainer', null=True),
        ),
        migrations.AlterField(
            model_name='locationpage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='public_locationpage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='locationpage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='public_locationpage_maintainer', null=True),
        ),
        migrations.AlterField(
            model_name='standardpage',
            name='editor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='public_standardpage_editor', null=True),
        ),
        migrations.AlterField(
            model_name='standardpage',
            name='page_maintainer',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='public_standardpage_maintainer', null=True),
        ),
    ]
