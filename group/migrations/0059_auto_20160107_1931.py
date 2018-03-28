# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0003_add_verbose_names'),
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('group', '0058_auto_20160107_1929'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupmeetingminutespagetable',
            name='link_document',
            field=models.ForeignKey(related_name='+', to='wagtaildocs.Document', null=True, blank=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='groupmeetingminutespagetable',
            name='link_external',
            field=models.URLField(verbose_name='External link', blank=True),
        ),
        migrations.AddField(
            model_name='groupmeetingminutespagetable',
            name='link_page',
            field=models.ForeignKey(related_name='+', to='wagtailcore.Page', null=True, blank=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='groupreportspagetable',
            name='link_document',
            field=models.ForeignKey(related_name='+', to='wagtaildocs.Document', null=True, blank=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='groupreportspagetable',
            name='link_external',
            field=models.URLField(verbose_name='External link', blank=True),
        ),
        migrations.AddField(
            model_name='groupreportspagetable',
            name='link_page',
            field=models.ForeignKey(related_name='+', to='wagtailcore.Page', null=True, blank=True, on_delete=models.CASCADE),
        ),
    ]
