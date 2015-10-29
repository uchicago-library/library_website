# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0017_auto_20151029_1818'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vcard',
            options={},
        ),
        migrations.RemoveField(
            model_name='vcard',
            name='email',
        ),
        migrations.RemoveField(
            model_name='vcard',
            name='phone_label',
        ),
        migrations.RemoveField(
            model_name='vcard',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='vcard',
            name='sort_order',
        ),
        migrations.AddField(
            model_name='staffpagepagevcards',
            name='sort_order',
            field=models.IntegerField(null=True, blank=True, editable=False),
        ),
    ]
