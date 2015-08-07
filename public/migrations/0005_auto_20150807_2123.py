# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailforms', '0002_add_verbose_names'),
        ('wagtailsearch', '0002_add_verbose_names'),
        ('wagtailredirects', '0002_add_verbose_names'),
        ('wagtailcore', '0001_squashed_0016_change_page_url_path_to_text_field'),
        ('public', '0004_remove_standardpage_foo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='standardpage',
            name='basepage_ptr',
        ),
        migrations.DeleteModel(
            name='StandardPage',
        ),
    ]
