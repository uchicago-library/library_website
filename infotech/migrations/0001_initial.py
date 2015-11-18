# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('staff', '0002_auto_20151113_2245'),
    ]

    operations = [
        migrations.CreateModel(
            name='InfoTechProjectPage',
            fields=[
                ('page_ptr', models.OneToOneField(serialize=False, parent_link=True, primary_key=True, to='wagtailcore.Page', auto_created=True)),
                ('last_reviewed', models.DateTimeField(verbose_name='Last Reviewed', null=True, blank=True)),
                ('sort_order', models.IntegerField(default=0, blank=True)),
                ('description', models.TextField()),
                ('requestor', models.CharField(max_length=255)),
                ('status', models.CharField(default='active', choices=[('active', 'Active'), ('pending', 'Pending'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('discussion', 'Discussion')], max_length=2)),
                ('editor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='infotech_infotechprojectpage_editor')),
                ('page_maintainer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', related_name='infotech_infotechprojectpage_maintainer')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
