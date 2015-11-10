# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('intranetbase', '0001_initial'),
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sidebarpage',
            name='editor',
            field=models.ForeignKey(related_name='intranetbase_sidebarpage_editor', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='sidebarpage',
            name='page_maintainer',
            field=models.ForeignKey(related_name='intranetbase_sidebarpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='plainpage',
            name='editor',
            field=models.ForeignKey(related_name='intranetbase_plainpage_editor', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='plainpage',
            name='page_maintainer',
            field=models.ForeignKey(related_name='intranetbase_plainpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
    ]
