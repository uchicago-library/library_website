# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib_collections', '0055_regionalcollectionplacements'),
    ]

    operations = [
        migrations.RenameField(
            model_name='regionalcollectionplacements',
            old_name='description',
            new_name='collection_description',
        ),
        migrations.RenameField(
            model_name='regionalcollectionplacements',
            old_name='name',
            new_name='collection_name',
        ),
    ]
