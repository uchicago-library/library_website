# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_auto_20150807_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basepage',
            name='last_reviewed',
            field=models.DateTimeField(blank=True, verbose_name='Did you review this page?', null=True),
        ),
    ]
