# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0009_remove_staffpage_is_subject_specialist'),
        ('public', '0037_auto_20151022_1854'),
    ]

    operations = [
        migrations.AddField(
            model_name='donorpage',
            name='content_specialist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='public_donorpage_content_specialist'),
        ),
        migrations.AddField(
            model_name='donorpage',
            name='editor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='public_donorpage_editor'),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='content_specialist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='public_locationpage_content_specialist'),
        ),
        migrations.AddField(
            model_name='locationpage',
            name='editor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='public_locationpage_editor'),
        ),
        migrations.AddField(
            model_name='standardpage',
            name='content_specialist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='public_standardpage_content_specialist'),
        ),
        migrations.AddField(
            model_name='standardpage',
            name='editor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='public_standardpage_editor'),
        ),
        migrations.AlterField(
            model_name='donorpage',
            name='page_maintainer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='public_donorpage_maintainer'),
        ),
        migrations.AlterField(
            model_name='locationpage',
            name='page_maintainer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='public_locationpage_maintainer'),
        ),
        migrations.AlterField(
            model_name='standardpage',
            name='page_maintainer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True, related_name='public_standardpage_maintainer'),
        ),
    ]
