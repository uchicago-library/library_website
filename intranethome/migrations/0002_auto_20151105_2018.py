# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),
        ('intranethome', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='intranethomepage',
            name='editor',
            field=models.ForeignKey(related_name='intranethome_intranethomepage_editor', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
        migrations.AddField(
            model_name='intranethomepage',
            name='last_reviewed',
            field=models.DateTimeField(null=True, verbose_name=b'Last Reviewed', blank=True),
        ),
        migrations.AddField(
            model_name='intranethomepage',
            name='page_maintainer',
            field=models.ForeignKey(related_name='intranethome_intranethomepage_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True),
        ),
    ]
