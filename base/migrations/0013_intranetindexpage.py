# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.wagtailimages.blocks
import base.models
import wagtail.wagtailcore.blocks
import django.db.models.deletion
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('staff', '0008_auto_20151213_2022'),
        ('base', '0012_auto_20151211_2102'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntranetIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, to='wagtailcore.Page', serialize=False, primary_key=True, auto_created=True)),
                ('start_sidebar_from_here', models.BooleanField(default=False)),
                ('show_sidebar', models.BooleanField(default=False)),
                ('last_reviewed', models.DateField(blank=True, null=True, verbose_name='Last Reviewed')),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('intro', wagtail.wagtailcore.fields.StreamField((('h2', wagtail.wagtailcore.blocks.CharBlock(icon='title', template='base/blocks/h2.html', classname='title')), ('h3', wagtail.wagtailcore.blocks.CharBlock(icon='title', template='base/blocks/h3.html', classname='title')), ('h4', wagtail.wagtailcore.blocks.CharBlock(icon='title', template='base/blocks/h4.html', classname='title')), ('h5', wagtail.wagtailcore.blocks.CharBlock(icon='title', template='base/blocks/h5.html', classname='title')), ('h6', wagtail.wagtailcore.blocks.CharBlock(icon='title', template='base/blocks/h6.html', classname='title')), ('paragraph', wagtail.wagtailcore.blocks.StructBlock((('paragraph', wagtail.wagtailcore.blocks.RichTextBlock()),))), ('image', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock()), ('citation', wagtail.wagtailcore.blocks.CharBlock(required=False)), ('caption', wagtail.wagtailcore.blocks.TextBlock(required=False)), ('alt_text', wagtail.wagtailcore.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock()), ('source', wagtail.wagtailcore.blocks.CharBlock(required=False)), ('lightbox', wagtail.wagtailcore.blocks.BooleanBlock(required=False, default=False))), label='Image')), ('blockquote', wagtail.wagtailcore.blocks.StructBlock((('quote', wagtail.wagtailcore.blocks.TextBlock('quote title')), ('attribution', wagtail.wagtailcore.blocks.CharBlock())))), ('code', wagtail.wagtailcore.blocks.StructBlock((('language', wagtail.wagtailcore.blocks.ChoiceBlock(choices=[('bash', 'Bash/Shell'), ('css', 'CSS'), ('html', 'HTML'), ('javascript', 'Javascript'), ('json', 'JSON'), ('ocaml', 'OCaml'), ('php5', 'PHP'), ('html+php', 'PHP/HTML'), ('python', 'Python'), ('scss', 'SCSS'), ('yaml', 'YAML')])), ('code', wagtail.wagtailcore.blocks.TextBlock()))))))),
                ('display_hierarchical_listing', models.BooleanField(default=False)),
                ('body', wagtail.wagtailcore.fields.StreamField((('h2', wagtail.wagtailcore.blocks.CharBlock(icon='title', template='base/blocks/h2.html', classname='title')), ('h3', wagtail.wagtailcore.blocks.CharBlock(icon='title', template='base/blocks/h3.html', classname='title')), ('h4', wagtail.wagtailcore.blocks.CharBlock(icon='title', template='base/blocks/h4.html', classname='title')), ('h5', wagtail.wagtailcore.blocks.CharBlock(icon='title', template='base/blocks/h5.html', classname='title')), ('h6', wagtail.wagtailcore.blocks.CharBlock(icon='title', template='base/blocks/h6.html', classname='title')), ('paragraph', wagtail.wagtailcore.blocks.StructBlock((('paragraph', wagtail.wagtailcore.blocks.RichTextBlock()),))), ('image', wagtail.wagtailcore.blocks.StructBlock((('image', wagtail.wagtailimages.blocks.ImageChooserBlock()), ('citation', wagtail.wagtailcore.blocks.CharBlock(required=False)), ('caption', wagtail.wagtailcore.blocks.TextBlock(required=False)), ('alt_text', wagtail.wagtailcore.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock()), ('source', wagtail.wagtailcore.blocks.CharBlock(required=False)), ('lightbox', wagtail.wagtailcore.blocks.BooleanBlock(required=False, default=False))), label='Image')), ('blockquote', wagtail.wagtailcore.blocks.StructBlock((('quote', wagtail.wagtailcore.blocks.TextBlock('quote title')), ('attribution', wagtail.wagtailcore.blocks.CharBlock())))), ('code', wagtail.wagtailcore.blocks.StructBlock((('language', wagtail.wagtailcore.blocks.ChoiceBlock(choices=[('bash', 'Bash/Shell'), ('css', 'CSS'), ('html', 'HTML'), ('javascript', 'Javascript'), ('json', 'JSON'), ('ocaml', 'OCaml'), ('php5', 'PHP'), ('html+php', 'PHP/HTML'), ('python', 'Python'), ('scss', 'SCSS'), ('yaml', 'YAML')])), ('code', wagtail.wagtailcore.blocks.TextBlock()))))))),
                ('editor', models.ForeignKey(to='staff.StaffPage', blank=True, related_name='base_intranetindexpage_editor', null=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('page_maintainer', models.ForeignKey(to='staff.StaffPage', blank=True, related_name='base_intranetindexpage_maintainer', null=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
