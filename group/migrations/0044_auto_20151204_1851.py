# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailsearch.index


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0043_auto_20151203_1806'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupMemberRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('text', models.CharField(max_length=255)),
            ],
            bases=(models.Model, wagtail.wagtailsearch.index.Indexed),
        ),
        migrations.AddField(
            model_name='groupmembers',
            name='role',
            field=models.ForeignKey(related_name='+', blank=True, to='group.GroupMemberRole', null=True),
        ),
    ]
