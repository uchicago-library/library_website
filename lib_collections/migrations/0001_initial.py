# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0001_squashed_0016_change_page_url_path_to_text_field'),
        ('public', '0024_auto_20151016_1541'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', primary_key=True, auto_created=True, parent_link=True, serialize=False)),
                ('description', models.TextField(blank=True)),
                ('last_reviewed', models.DateTimeField(blank=True, null=True, verbose_name='Last Reviewed')),
                ('short_abstract', models.TextField()),
                ('location', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True, to='public.LocationPage', related_name='lib_collections_collectionpage_related')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='CollectionPageAccessLinks',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('access_link_label', models.CharField(max_length=255)),
                ('access_link_url', models.URLField(blank=True, verbose_name='External link')),
                ('page', modelcluster.fields.ParentalKey(to='lib_collections.CollectionPage', related_name='access_links')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
