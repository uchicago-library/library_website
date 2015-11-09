# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0008_image_created_at_index'),
        ('public', '0001_initial'),
        ('staff', '0001_initial'),
        ('lib_collections', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjectspecialistplacement',
            name='subject_specialist',
            field=models.ForeignKey(related_name='subject_specialist', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='relatedcollectionpageplacement',
            name='parent',
            field=modelcluster.fields.ParentalKey(related_name='related_collection_placement', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='lib_collections.CollectionPage', null=True),
        ),
        migrations.AddField(
            model_name='relatedcollectionpageplacement',
            name='related_collection',
            field=models.ForeignKey(related_name='related_collection', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='lib_collections.CollectionPage', null=True),
        ),
        migrations.AddField(
            model_name='regionalcollectionplacements',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='regional_collections', to='lib_collections.CollectingAreaPage'),
        ),
        migrations.AddField(
            model_name='highlightedcollectionsplacement',
            name='collection',
            field=models.ForeignKey(related_name='highlighted_collections', on_delete=django.db.models.deletion.SET_NULL, to='lib_collections.CollectionPage', null=True),
        ),
        migrations.AddField(
            model_name='highlightedcollectionsplacement',
            name='parent',
            field=modelcluster.fields.ParentalKey(related_name='highlighted_collection_placements', on_delete=django.db.models.deletion.SET_NULL, to='lib_collections.CollectingAreaPage', null=True),
        ),
        migrations.AddField(
            model_name='donorpageplacement',
            name='donor',
            field=models.ForeignKey(related_name='donor_page', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='public.DonorPage', null=True),
        ),
        migrations.AddField(
            model_name='donorpageplacement',
            name='parent',
            field=modelcluster.fields.ParentalKey(related_name='donor_page_list_placement', on_delete=django.db.models.deletion.SET_NULL, to='lib_collections.CollectionPage', null=True),
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
        migrations.AddField(
            model_name='collectionpagealternatenames',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='alternate_name', to='lib_collections.CollectionPage'),
        ),
        migrations.AddField(
            model_name='collectionpageaccesslinks',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='access_links', to='lib_collections.CollectionPage'),
        ),
        migrations.AddField(
            model_name='collectionpage',
            name='collection_location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='public.LocationPage', null=True),
        ),
        migrations.AddField(
            model_name='collectionpage',
            name='content_specialist',
            field=models.ForeignKey(related_name='lib_collections_collectionpage_content_specialist', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='collectionpage',
            name='editor',
            field=models.ForeignKey(related_name='lib_collections_collectionpage_editor', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='collectionpage',
            name='page_maintainer',
            field=models.ForeignKey(related_name='lib_collections_collectionpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='collectionpage',
            name='staff_contact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='collectionpage',
            name='thumbnail',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtailimages.Image', null=True),
        ),
    ]
