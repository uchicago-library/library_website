# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_basepage_standardpage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basepage',
            name='last_reviewed',
            field=models.DateTimeField(blank=True, verbose_name='Did you review this page?'),
        ),
    ]
