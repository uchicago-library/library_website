# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0057_auto_20151229_1635'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupmeetingminutespagetable',
            name='document',
        ),
        migrations.RemoveField(
            model_name='groupmeetingminutespagetable',
            name='link',
        ),
        migrations.RemoveField(
            model_name='groupreportspagetable',
            name='document',
        ),
        migrations.RemoveField(
            model_name='groupreportspagetable',
            name='link',
        ),
    ]
