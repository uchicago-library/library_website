# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields
import wagtail.wagtailcore.blocks
import wagtail.wagtailimages.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0015_auto_20150807_2056'),
        ('public', '0005_auto_20150807_2123'),
    ]

    operations = [
        migrations.CreateModel(
            name='StandardPage',
            fields=[
                ('basepage_ptr', models.OneToOneField(auto_created=True, to='base.BasePage', serialize=False, parent_link=True, primary_key=True)),
                ('body', wagtail.wagtailcore.fields.StreamField((('heading', wagtail.wagtailcore.blocks.CharBlock(classname='full title')), ('paragraph', wagtail.wagtailcore.blocks.RichTextBlock()), ('image', wagtail.wagtailimages.blocks.ImageChooserBlock())))),
            ],
            options={
                'abstract': False,
            },
            bases=('base.basepage',),
        ),
    ]
