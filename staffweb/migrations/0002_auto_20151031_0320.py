# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailredirects', '0002_add_verbose_names'),
        ('wagtailforms', '0002_add_verbose_names'),
        ('staff', '0037_auto_20151031_0320'),
        ('wagtailsearchpromotions', '0001_initial'),
        ('wagtailcore', '0019_verbose_names_cleanup'),
        ('staffweb', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupcommitteepage',
            name='page_ptr',
        ),
        migrations.DeleteModel(
            name='GroupCommitteePage',
        ),
    ]
