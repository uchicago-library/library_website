# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailsearch', '0002_add_verbose_names'),
        ('wagtailcore', '0001_squashed_0016_change_page_url_path_to_text_field'),
        ('wagtailforms', '0002_add_verbose_names'),
        ('wagtailredirects', '0002_add_verbose_names'),
        ('base', '0006_remove_basepage_last_reviewed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basepage',
            name='page_ptr',
        ),
        migrations.RemoveField(
            model_name='standardpage',
            name='basepage_ptr',
        ),
        migrations.DeleteModel(
            name='BasePage',
        ),
        migrations.DeleteModel(
            name='StandardPage',
        ),
    ]
