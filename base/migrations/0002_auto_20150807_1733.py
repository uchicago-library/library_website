# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailsearch', '0002_add_verbose_names'),
        ('wagtailforms', '0002_add_verbose_names'),
        ('wagtailcore', '0001_squashed_0016_change_page_url_path_to_text_field'),
        ('wagtailredirects', '0002_add_verbose_names'),
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StandardPage',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, serialize=False, to='wagtailcore.Page')),
                ('description', models.TextField()),
                ('foo', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
        migrations.RemoveField(
            model_name='basepage',
            name='page_ptr',
        ),
        migrations.DeleteModel(
            name='BasePage',
        ),
    ]
