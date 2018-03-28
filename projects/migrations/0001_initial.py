# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('staff', '0000_manual_pre_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, auto_created=True, to='wagtailcore.Page', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='ProjectPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, auto_created=True, to='wagtailcore.Page', on_delete=models.CASCADE)),
                ('last_reviewed', models.DateField(verbose_name='Last Reviewed', blank=True, null=True)),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('description', models.TextField()),
                ('requestor', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=55, default='active', choices=[('active', 'Active'), ('pending', 'Pending'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('discussion', 'Discussion')])),
                ('size', models.CharField(max_length=55, default='small', choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')])),
                ('staff', models.CharField(max_length=255, blank=True)),
                ('date_added_to_list', models.DateField(default=django.utils.timezone.now)),
                ('completion', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('editor', models.ForeignKey(related_name='projects_projectpage_editor', to='staff.StaffPage', on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('page_maintainer', models.ForeignKey(related_name='projects_projectpage_maintainer', to='staff.StaffPage', on_delete=django.db.models.deletion.SET_NULL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
