# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0012_remove_staffpage_email'),
    ]

    operations = [
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
    ]
