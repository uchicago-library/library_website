# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0009_remove_staffpage_is_subject_specialist'),
        ('lib_collections', '0056_auto_20151026_2036'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectingareapage',
            name='content_specialist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='lib_collections_collectingareapage_content_specialist'),
        ),
        migrations.AddField(
            model_name='collectingareapage',
            name='editor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='lib_collections_collectingareapage_editor'),
        ),
        migrations.AddField(
            model_name='collectionpage',
            name='content_specialist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='lib_collections_collectionpage_content_specialist'),
        ),
        migrations.AddField(
            model_name='collectionpage',
            name='editor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='lib_collections_collectionpage_editor'),
        ),
        migrations.AlterField(
            model_name='collectingareapage',
            name='page_maintainer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='lib_collections_collectingareapage_maintainer'),
        ),
        migrations.AlterField(
            model_name='collectionpage',
            name='page_maintainer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='lib_collections_collectionpage_maintainer'),
        ),
    ]
