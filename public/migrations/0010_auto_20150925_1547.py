# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_remove_basepage_location'),
        ('wagtailsearch', '0002_add_verbose_names'),
        ('wagtailredirects', '0002_add_verbose_names'),
        ('wagtailcore', '0001_squashed_0016_change_page_url_path_to_text_field'),
        ('wagtailforms', '0002_add_verbose_names'),
        ('public', '0009_locationpage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='locationpage',
            name='basepage_ptr',
        ),
        migrations.DeleteModel(
            name='LocationPage',
        ),
    ]
