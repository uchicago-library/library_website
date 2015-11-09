# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),
        ('wagtailredirects', '0002_add_verbose_names'),
        ('wagtailforms', '0002_add_verbose_names'),
        ('wagtailcore', '0019_verbose_names_cleanup'),
        ('wagtailsearchpromotions', '0001_initial'),
        ('intranetbase', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlainPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('last_reviewed', models.DateTimeField(null=True, verbose_name=b'Last Reviewed', blank=True)),
                ('body', wagtail.wagtailcore.fields.RichTextField()),
                ('editor', models.ForeignKey(related_name='intranetbase_plainpage_editor', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True)),
                ('page_maintainer', models.ForeignKey(related_name='intranetbase_plainpage_maintainer', on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffPage', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.RemoveField(
            model_name='intranetpage',
            name='editor',
        ),
        migrations.RemoveField(
            model_name='intranetpage',
            name='page_maintainer',
        ),
        migrations.RemoveField(
            model_name='intranetpage',
            name='page_ptr',
        ),
        migrations.DeleteModel(
            name='IntranetPage',
        ),
    ]
