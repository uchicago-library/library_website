# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('wagtailsearchpromotions', '0001_initial'),
        ('wagtailforms', '0002_add_verbose_names'),
        ('wagtailredirects', '0004_set_unique_on_path_and_site'),
        ('base', '0005_auto_20151125_1427'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='intranetsidebarpage',
            name='editor',
        ),
        migrations.RemoveField(
            model_name='intranetsidebarpage',
            name='page_maintainer',
        ),
        migrations.RemoveField(
            model_name='intranetsidebarpage',
            name='page_ptr',
        ),
        migrations.DeleteModel(
            name='IntranetSidebarPage',
        ),
    ]
