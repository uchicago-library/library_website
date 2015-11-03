# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailsearch.index
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0019_verbose_names_cleanup'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('description', models.TextField(blank=True)),
                ('last_reviewed', models.DateTimeField(null=True, verbose_name=b'Last Reviewed', blank=True)),
                ('short_abstract', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='CollectionPageAccessLinks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('access_link_label', models.CharField(max_length=255)),
                ('access_link_url', models.URLField(verbose_name=b'Access link URL')),
                ('page', modelcluster.fields.ParentalKey(related_name='access_links', to='lib_collections.CollectionPage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CollectionPageFormatPlacement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
            ],
            options={
                'verbose_name': 'Collection Placement',
                'verbose_name_plural': 'Collection Placements',
            },
        ),
        migrations.CreateModel(
            name='Format',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=255)),
            ],
            bases=(models.Model, wagtail.wagtailsearch.index.Indexed),
        ),
        migrations.AddField(
            model_name='collectionpageformatplacement',
            name='format',
            field=models.ForeignKey(related_name='+', to='lib_collections.Format'),
        ),
        migrations.AddField(
            model_name='collectionpageformatplacement',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='collection_placements', to='lib_collections.CollectionPage'),
        ),
    ]
