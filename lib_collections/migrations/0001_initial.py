# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailsearch.index
import modelcluster.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectingAreaPage',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, to='wagtailcore.Page', auto_created=True)),
                ('last_reviewed', models.DateTimeField(verbose_name='Last Reviewed', blank=True, null=True)),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('guide_link_text', models.CharField(max_length=255, default='')),
                ('guide_link_url', models.URLField(verbose_name='Libguide URL', default='')),
                ('collecting_statement', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
        migrations.CreateModel(
            name='CollectingAreaPageLibGuides',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('guide_link_text', models.CharField(max_length=255, default='')),
                ('guide_link_url', models.URLField(verbose_name='Libguide URL', default='')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CollectingAreaPageStacksRanges',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('stacks_range', models.CharField(max_length=100, blank=True)),
                ('stacks_URL', models.URLField(max_length=254, default='', blank=True)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CollectingAreaReferenceLocationPlacement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CollectionPage',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, primary_key=True, parent_link=True, to='wagtailcore.Page', auto_created=True)),
                ('last_reviewed', models.DateTimeField(verbose_name='Last Reviewed', blank=True, null=True)),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('short_abstract', models.TextField(default='')),
                ('full_description', models.TextField(default='')),
                ('access_instructions', models.TextField(blank=True, default='')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='CollectionPageAccessLinks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('access_link_label', models.CharField(max_length=255)),
                ('access_link_url', models.URLField(verbose_name='Access link URL')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CollectionPageAlternateNames',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('alternate_name', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CollectionPageFormatPlacement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Collection Placement',
                'verbose_name_plural': 'Collection Placements',
            },
        ),
        migrations.CreateModel(
            name='CollectionPageSubjectPlacement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Subject Placement',
                'verbose_name_plural': 'Subbject Placements',
            },
        ),
        migrations.CreateModel(
            name='DonorPagePlacement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Format',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('text', models.CharField(max_length=255)),
            ],
            bases=(models.Model, wagtail.wagtailsearch.index.Indexed),
        ),
        migrations.CreateModel(
            name='HighlightedCollectionsPlacement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RegionalCollectionPlacements',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('collection_name', models.CharField(max_length=254, blank=True)),
                ('collection_description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RelatedCollectionPagePlacement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubjectSpecialistPlacement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('parent', modelcluster.fields.ParentalKey(to='lib_collections.CollectingAreaPage', on_delete=django.db.models.deletion.SET_NULL, related_name='subject_specialist_placement', blank=True, null=True)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
