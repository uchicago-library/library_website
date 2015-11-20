# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0013_remove_locationpage_library_floorplan_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationpage',
            name='library_floorplan_link',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='public.FloorPlanPage', null=True),
        ),
    ]
