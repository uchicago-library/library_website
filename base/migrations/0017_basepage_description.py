# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0016_remove_basepage_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='basepage',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
    ]
