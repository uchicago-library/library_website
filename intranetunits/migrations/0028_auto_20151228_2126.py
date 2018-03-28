# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wagtail.core.fields
import wagtail.embeds.blocks
import wagtail.images.blocks
import wagtail.core.blocks
import base.models


class Migration(migrations.Migration):

    dependencies = [
        ('intranetunits', '0027_auto_20151218_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intranetunitspage',
            name='body',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h2.html')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h3.html')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h4.html')), ('h5', wagtail.core.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h5.html')), ('h6', wagtail.core.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h6.html')), ('paragraph', wagtail.core.blocks.StructBlock((('paragraph', wagtail.core.blocks.RichTextBlock()),))), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('citation', wagtail.core.blocks.CharBlock(required=False)), ('caption', wagtail.core.blocks.TextBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock()), ('source', wagtail.core.blocks.CharBlock(required=False)), ('lightbox', wagtail.core.blocks.BooleanBlock(required=False, default=False))), label='Image')), ('blockquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock())))), ('video', wagtail.embeds.blocks.EmbedBlock(icon='media')), ('code', wagtail.core.blocks.StructBlock((('language', wagtail.core.blocks.ChoiceBlock(choices=[('bash', 'Bash/Shell'), ('css', 'CSS'), ('html', 'HTML'), ('javascript', 'Javascript'), ('json', 'JSON'), ('ocaml', 'OCaml'), ('php5', 'PHP'), ('html+php', 'PHP/HTML'), ('python', 'Python'), ('scss', 'SCSS'), ('yaml', 'YAML')])), ('code', wagtail.core.blocks.TextBlock()))))), blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='intranetunitspage',
            name='intro',
            field=wagtail.core.fields.StreamField((('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h2.html')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h3.html')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h4.html')), ('h5', wagtail.core.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h5.html')), ('h6', wagtail.core.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h6.html')), ('paragraph', wagtail.core.blocks.StructBlock((('paragraph', wagtail.core.blocks.RichTextBlock()),))), ('image', wagtail.core.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('citation', wagtail.core.blocks.CharBlock(required=False)), ('caption', wagtail.core.blocks.TextBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(required=False)), ('alignment', base.models.ImageFormatChoiceBlock()), ('source', wagtail.core.blocks.CharBlock(required=False)), ('lightbox', wagtail.core.blocks.BooleanBlock(required=False, default=False))), label='Image')), ('blockquote', wagtail.core.blocks.StructBlock((('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock())))), ('video', wagtail.embeds.blocks.EmbedBlock(icon='media')), ('code', wagtail.core.blocks.StructBlock((('language', wagtail.core.blocks.ChoiceBlock(choices=[('bash', 'Bash/Shell'), ('css', 'CSS'), ('html', 'HTML'), ('javascript', 'Javascript'), ('json', 'JSON'), ('ocaml', 'OCaml'), ('php5', 'PHP'), ('html+php', 'PHP/HTML'), ('python', 'Python'), ('scss', 'SCSS'), ('yaml', 'YAML')])), ('code', wagtail.core.blocks.TextBlock()))))), blank=True),
        ),
    ]
