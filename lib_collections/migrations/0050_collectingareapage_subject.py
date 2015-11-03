# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0002_auto_20151022_1913'),
        ('lib_collections', '0049_auto_20151023_2035'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectingareapage',
            name='subject',
            field=models.ForeignKey(related_name='lib_collections_collectingareapage_related', on_delete=django.db.models.deletion.SET_NULL, to='subjects.Subject', null=True),
        ),
    ]
