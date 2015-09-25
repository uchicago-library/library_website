# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailredirects', '0002_add_verbose_names'),
        ('wagtailcore', '0001_squashed_0016_change_page_url_path_to_text_field'),
        ('wagtailsearch', '0002_add_verbose_names'),
        ('wagtailforms', '0002_add_verbose_names'),
        ('base', '0019_remove_basepage_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basepage',
            name='page_ptr',
        ),
        migrations.DeleteModel(
            name='BasePage',
        ),
    ]
