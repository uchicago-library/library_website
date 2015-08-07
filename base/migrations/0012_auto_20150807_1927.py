# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_auto_20150807_1925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basepage',
            name='last_reviewed',
            field=models.DateTimeField(null=True, verbose_name='Did you review this page?', blank=True),
        ),
    ]
