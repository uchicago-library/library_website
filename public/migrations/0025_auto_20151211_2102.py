# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.fields
import wagtail.blocks
import base.models
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0024_auto_20151209_2251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standardpage',
            name='body',
            field=wagtail.fields.StreamField((('h2', wagtail.blocks.CharBlock(template='base/blocks/h2.html', classname='title', icon='title')), ('h3', wagtail.blocks.CharBlock(template='base/blocks/h3.html', classname='title', icon='title')), ('h4', wagtail.blocks.CharBlock(template='base/blocks/h4.html', classname='title', icon='title')), ('h5', wagtail.blocks.CharBlock(template='base/blocks/h5.html', classname='title', icon='title')), ('h6', wagtail.blocks.CharBlock(template='base/blocks/h6.html', classname='title', icon='title')), ('paragraph', wagtail.blocks.StructBlock((('paragraph', wagtail.blocks.RichTextBlock()),))), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('citation', wagtail.blocks.CharBlock(required=False)), ('caption', wagtail.blocks.TextBlock(required=False)), ('alt_text', wagtail.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock()), ('source', wagtail.blocks.CharBlock(required=False)), ('lightbox', wagtail.blocks.BooleanBlock(required=False, default=False))), label='Image')), ('blockquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('attribution', wagtail.blocks.CharBlock())))), ('code', wagtail.blocks.StructBlock((('language', wagtail.blocks.ChoiceBlock(choices=[('bash', 'Bash/Shell'), ('css', 'CSS'), ('html', 'HTML'), ('javascript', 'Javascript'), ('json', 'JSON'), ('ocaml', 'OCaml'), ('php5', 'PHP'), ('html+php', 'PHP/HTML'), ('python', 'Python'), ('scss', 'SCSS'), ('yaml', 'YAML')])), ('code', wagtail.blocks.TextBlock())))))),
        ),
    ]
