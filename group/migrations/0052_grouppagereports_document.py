# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0003_add_verbose_names'),
        ('group', '0051_auto_20151204_2210'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouppagereports',
            name='document',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True, to='wagtaildocs.Document', related_name='+'),
        ),
    ]
