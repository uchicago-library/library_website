# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0003_add_verbose_names'),
        ('group', '0049_auto_20151204_2148'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouppagemeetingminutes',
            name='document',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True, to='wagtaildocs.Document'),
        ),
    ]
