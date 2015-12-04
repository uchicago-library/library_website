# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0003_add_verbose_names'),
        ('intranetunits', '0021_auto_20151204_1927'),
    ]

    operations = [
        migrations.AddField(
            model_name='intranetunitpagereports',
            name='document',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True, to='wagtaildocs.Document', related_name='+'),
        ),
    ]
