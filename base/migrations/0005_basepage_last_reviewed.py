# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_standardpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='basepage',
            name='last_reviewed',
            field=models.DateField(blank=True, verbose_name='Check if you reviewed the content?', default=datetime.datetime(2015, 8, 7, 17, 55, 17, 289527, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
