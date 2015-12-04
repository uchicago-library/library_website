# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0050_grouppagemeetingminutes_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouppagemeetingminutes',
            name='link',
            field=models.URLField(default='', blank=True, max_length=254),
        ),
    ]
