# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.images.blocks
import base.models
import wagtail.blocks
import django.db.models.deletion
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('staff', '0000_manual_pre_initial'),
        ('base', '0012_auto_20151211_2102'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntranetIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, to='wagtailcore.Page', serialize=False, primary_key=True, auto_created=True, on_delete=models.CASCADE)),
                ('start_sidebar_from_here', models.BooleanField(default=False)),
                ('show_sidebar', models.BooleanField(default=False)),
                ('last_reviewed', models.DateField(blank=True, null=True, verbose_name='Last Reviewed')),
                ('sort_order', models.IntegerField(blank=True, default=0)),
                ('intro', wagtail.fields.StreamField((('h2', wagtail.blocks.CharBlock(icon='title', template='base/blocks/h2.html', classname='title')), ('h3', wagtail.blocks.CharBlock(icon='title', template='base/blocks/h3.html', classname='title')), ('h4', wagtail.blocks.CharBlock(icon='title', template='base/blocks/h4.html', classname='title')), ('h5', wagtail.blocks.CharBlock(icon='title', template='base/blocks/h5.html', classname='title')), ('h6', wagtail.blocks.CharBlock(icon='title', template='base/blocks/h6.html', classname='title')), ('paragraph', wagtail.blocks.StructBlock((('paragraph', wagtail.blocks.RichTextBlock()),))), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('citation', wagtail.blocks.CharBlock(required=False)), ('caption', wagtail.blocks.TextBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock()), ('source', wagtail.blocks.CharBlock(required=False)), ('lightbox', wagtail.blocks.BooleanBlock(required=False, default=False))), label='Image')), ('blockquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('attribution', wagtail.blocks.CharBlock())))), ('code', wagtail.blocks.StructBlock((('language', wagtail.blocks.ChoiceBlock(choices=[('bash', 'Bash/Shell'), ('css', 'CSS'), ('html', 'HTML'), ('javascript', 'Javascript'), ('json', 'JSON'), ('ocaml', 'OCaml'), ('php5', 'PHP'), ('html+php', 'PHP/HTML'), ('python', 'Python'), ('scss', 'SCSS'), ('yaml', 'YAML')])), ('code', wagtail.blocks.TextBlock()))))))),
                ('display_hierarchical_listing', models.BooleanField(default=False)),
                ('body', wagtail.fields.StreamField((('h2', wagtail.blocks.CharBlock(icon='title', template='base/blocks/h2.html', classname='title')), ('h3', wagtail.blocks.CharBlock(icon='title', template='base/blocks/h3.html', classname='title')), ('h4', wagtail.blocks.CharBlock(icon='title', template='base/blocks/h4.html', classname='title')), ('h5', wagtail.blocks.CharBlock(icon='title', template='base/blocks/h5.html', classname='title')), ('h6', wagtail.blocks.CharBlock(icon='title', template='base/blocks/h6.html', classname='title')), ('paragraph', wagtail.blocks.StructBlock((('paragraph', wagtail.blocks.RichTextBlock()),))), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('citation', wagtail.blocks.CharBlock(required=False)), ('caption', wagtail.blocks.TextBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock()), ('source', wagtail.blocks.CharBlock(required=False)), ('lightbox', wagtail.blocks.BooleanBlock(required=False, default=False))), label='Image')), ('blockquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('attribution', wagtail.blocks.CharBlock())))), ('code', wagtail.blocks.StructBlock((('language', wagtail.blocks.ChoiceBlock(choices=[('bash', 'Bash/Shell'), ('css', 'CSS'), ('html', 'HTML'), ('javascript', 'Javascript'), ('json', 'JSON'), ('ocaml', 'OCaml'), ('php5', 'PHP'), ('html+php', 'PHP/HTML'), ('python', 'Python'), ('scss', 'SCSS'), ('yaml', 'YAML')])), ('code', wagtail.blocks.TextBlock()))))))),
                ('editor', models.ForeignKey(to='staff.StaffPage', blank=True, related_name='base_intranetindexpage_editor', null=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('page_maintainer', models.ForeignKey(to='staff.StaffPage', blank=True, related_name='base_intranetindexpage_maintainer', null=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
