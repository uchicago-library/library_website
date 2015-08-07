# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_auto_20150807_2049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basepage',
            name='last_reviewed',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Last Reviewed'),
        ),
    ]
