# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-08 20:59
from __future__ import unicode_literals

import base.models
import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import wagtail.contrib.table_block.blocks
import wagtail.blocks
import wagtail.fields
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.images.blocks
import wagtail.search.index


class Migration(migrations.Migration):

    replaces = [('news', '0001_initial'), ('news', '0002_auto_20151113_2245'), ('news', '0003_auto_20151118_2143'), ('news', '0004_auto_20151119_1737'), ('news', '0005_auto_20151119_1749'), ('news', '0006_auto_20151119_1832'), ('news', '0007_auto_20151119_1835'), ('news', '0008_auto_20151119_1851'), ('news', '0009_auto_20151119_2124'), ('news', '0010_auto_20151119_2133'), ('news', '0011_auto_20151123_1749'), ('news', '0012_auto_20151123_1752'), ('news', '0013_auto_20151124_0007'), ('news', '0014_auto_20151124_0008'), ('news', '0015_auto_20151201_2209'), ('news', '0016_auto_20151202_1651'), ('news', '0017_auto_20151203_1806'), ('news', '0018_auto_20151203_2258'), ('news', '0019_auto_20151204_1920'), ('news', '0020_auto_20151204_1927'), ('news', '0021_auto_20151209_2251'), ('news', '0022_auto_20151211_2102'), ('news', '0023_auto_20151218_2147'), ('news', '0024_auto_20151228_2126'), ('news', '0025_auto_20160119_1942'), ('news', '0026_auto_20160202_2247'), ('news', '0027_auto_20160202_2251'), ('news', '0028_auto_20160202_2253'), ('news', '0029_auto_20160202_2255'), ('news', '0030_auto_20160203_2233'), ('news', '0031_auto_20160204_1737'), ('news', '0032_auto_20160204_1757'), ('news', '0033_auto_20160204_1810'), ('news', '0034_auto_20160204_1828'), ('news', '0035_auto_20160205_1921'), ('news', '0036_auto_20160205_1925'), ('news', '0037_auto_20160223_2100'), ('news', '0038_auto_20160328_1905'), ('news', '0039_newspage_alt_text'), ('news', '0040_auto_20160602_1653'), ('news', '0041_auto_20160602_2028'), ('news', '0042_auto_20160609_2056'), ('news', '0043_auto_20160609_2105'), ('news', '0044_auto_20160609_2121'), ('news', '0045_auto_20160610_1600'), ('news', '0046_auto_20160812_1406'), ('news', '0047_newsemailaddition'), ('news', '0048_newsemailaddition_name'), ('news', '0049_auto_20160906_1516'), ('news', '0050_auto_20160907_1049'), ('news', '0051_auto_20160907_1059'), ('news', '0052_auto_20160907_1106'), ('news', '0053_auto_20160908_1018'), ('news', '0054_auto_20160908_1039'), ('news', '0055_auto_20160909_1312'), ('news', '0056_auto_20160912_1227'), ('news', '0057_auto_20160912_1354'), ('news', '0058_auto_20160913_1024'), ('news', '0059_auto_20160929_1632'), ('news', '0060_auto_20160930_1137'), ('news', '0061_auto_20160930_1327'), ('news', '0062_auto_20161014_1113'), ('news', '0063_auto_20161103_1604'), ('news', '0064_auto_20161104_1314')]

    initial = True

    dependencies = [
        ('wagtailcore', '0020_add_index_on_page_first_published_at'),
        ('wagtailimages', '0008_image_created_at_index'),
        ('staff', '0000_manual_pre_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('intro', wagtail.fields.RichTextField()),
                ('editor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='news_newsindexpage_editor', to='staff.StaffPage')),
                ('last_reviewed', models.DateField(blank=True, null=True, verbose_name='Last Reviewed')),
                ('page_maintainer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='news_newsindexpage_maintainer', to='staff.StaffPage')),
                ('show_sidebar', models.BooleanField(default=False)),
                ('start_sidebar_from_here', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='NewsPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('last_reviewed', models.DateField(blank=True, null=True, verbose_name='Last Reviewed')),
                ('excerpt', wagtail.fields.RichTextField(blank=True, help_text='Shown on the News feed. Populated automatically from “Body” if left empty.', null=True)),
                ('body', wagtail.fields.StreamField((('h2', wagtail.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h2.html')), ('h3', wagtail.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h3.html')), ('h4', wagtail.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h4.html')), ('h5', wagtail.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h5.html')), ('h6', wagtail.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h6.html')), ('paragraph', wagtail.blocks.StructBlock((('paragraph', wagtail.blocks.RichTextBlock()),))), ('image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('title', wagtail.blocks.CharBlock(required=False)), ('citation', wagtail.blocks.CharBlock(help_text='Photographer, artist, or creator of image', required=False)), ('caption', wagtail.blocks.TextBlock(help_text='Details about or description of image', required=False)), ('alt_text', wagtail.blocks.CharBlock(help_text='Invisible text for screen readers', required=False)), ('alignment', base.models.ImageFormatChoiceBlock()), ('source', wagtail.blocks.URLBlock(help_text='Link to image source (needed for Creative Commons)', required=False)), ('lightbox', wagtail.blocks.BooleanBlock(default=False, help_text='Link to a larger version of the image', required=False))), label='Image')), ('blockquote', wagtail.blocks.StructBlock((('quote', wagtail.blocks.TextBlock('quote title')), ('attribution', wagtail.blocks.CharBlock(required=False))))), ('button', wagtail.blocks.StructBlock((('button_type', wagtail.blocks.ChoiceBlock(choices=[('btn-primary', 'Primary'), ('btn-default', 'Secondary'), ('btn-reserve', 'Reservation')], default='btn-primary')), ('button_text', wagtail.blocks.CharBlock(max_length=20)), ('link_external', wagtail.blocks.URLBlock(required=False)), ('link_page', wagtail.blocks.PageChooserBlock(required=False)), ('link_document', wagtail.documents.blocks.DocumentChooserBlock(required=False))))), ('video', wagtail.embeds.blocks.EmbedBlock(icon='media')), ('code', wagtail.blocks.StructBlock((('language', wagtail.blocks.ChoiceBlock(choices=[('bash', 'Bash/Shell'), ('css', 'CSS'), ('html', 'HTML'), ('javascript', 'Javascript'), ('json', 'JSON'), ('ocaml', 'OCaml'), ('php5', 'PHP'), ('html+php', 'PHP/HTML'), ('python', 'Python'), ('scss', 'SCSS'), ('yaml', 'YAML')])), ('code', wagtail.blocks.TextBlock())))), ('agenda_item', wagtail.blocks.StructBlock((('start_time', wagtail.blocks.TimeBlock(icon='time', required=False)), ('end_time', wagtail.blocks.TimeBlock(icon='time', required=False)), ('session_title', wagtail.blocks.CharBlock(help_text='Title of the session.             Can be used as title of the talk in some situations.', icon='title', required=False)), ('event', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock((('title', wagtail.blocks.CharBlock(help_text='Talk title, workshop title, etc.', required=False)), ('presenters', wagtail.blocks.CharBlock(help_text='Comma separated list of presenters             (if more than one)', required=False)), ('room_number', wagtail.blocks.CharBlock(required=False)), ('description', wagtail.blocks.RichTextBlock(required=False)))), help_text='A talk or event with a title, presenter             room number, and description', icon='edit', label=' '))), icon='date', template='base/blocks/agenda.html')), ('clear', wagtail.blocks.StructBlock(())), ('table', wagtail.contrib.table_block.blocks.TableBlock(help_text='Right + click in a table cell for more options. Use <em>text</em> for italics, <strong>text</strong> for bold, and <a href="https://duckduckgo.com">text</a> for links.', table_options={'autoColumnSize': False, 'colHeaders': False, 'contextMenu': True, 'editor': 'text', 'height': 108, 'language': 'en', 'minSpareRows': 0, 'renderer': 'html', 'rowHeaders': False, 'startCols': 3, 'startRows': 3, 'stretchH': 'all'}, template='base/blocks/table.html')), ('staff_listing', wagtail.blocks.StructBlock((('staff_listing', wagtail.blocks.ListBlock(wagtail.blocks.PageChooserBlock(), help_text='Be sure to select staff pages from Loop.', icon='edit', label='Staff listing')), ('show_photos', wagtail.blocks.BooleanBlock(default=False, help_text='Show staff photographs.', required=False)), ('show_contact_info', wagtail.blocks.BooleanBlock(default=False, help_text='Show contact information.', required=False)), ('show_subject_specialties', wagtail.blocks.BooleanBlock(default=False, help_text='Show subject specialties.', required=False))), icon='group', template='base/blocks/staff_listing.html')), ('solo_image', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('citation', wagtail.blocks.RichTextBlock(blank=True, null=True)), ('caption', wagtail.blocks.RichTextBlock(blank=True, null=True, required=False)), ('alt_text', wagtail.blocks.CharBlock(help_text='Invisible text for screen readers', required=False))), help_text='Single image with caption on the right')), ('duo_image', wagtail.blocks.StructBlock((('image_one', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('citation', wagtail.blocks.RichTextBlock(blank=True, null=True)), ('caption', wagtail.blocks.RichTextBlock(blank=True, null=True, required=False)), ('alt_text', wagtail.blocks.CharBlock(help_text='Invisible text for screen readers', required=False))), help_text='First of two images displayed             side by side')), ('image_two', wagtail.blocks.StructBlock((('image', wagtail.images.blocks.ImageChooserBlock()), ('citation', wagtail.blocks.RichTextBlock(blank=True, null=True)), ('caption', wagtail.blocks.RichTextBlock(blank=True, null=True, required=False)), ('alt_text', wagtail.blocks.CharBlock(help_text='Invisible text for screen readers', required=False))), help_text='Second of two images displayed             side by side'))), help_text='Two images stacked side by side'))))),
                ('story_date', models.DateField(default=django.utils.timezone.now, help_text='If you use Settings to publish a future post, put the publish date here. Otherwise, leave today as the story date.')),
                ('sticky_until', models.DateField(blank=True, help_text='To be used by Admin and HR only.', null=True)),
                ('editor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='news_newspage_editor', to='staff.StaffPage')),
                ('page_maintainer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='news_newspage_maintainer', to='staff.StaffPage')),
                ('thumbnail', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
                ('show_sidebar', models.BooleanField(default=False)),
                ('start_sidebar_from_here', models.BooleanField(default=False)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='news_stories', to='staff.StaffPage')),
                ('alt_text', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='NewsEmailAddition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', wagtail.fields.RichTextField(help_text='Text to include in emails. This can include internal or external links.')),
                ('include_in_email_dated', models.DateField(default=datetime.datetime.now, help_text='Emails are send automatically via cron. Only email additions with the appropriate date will be attached to messages.')),
            ],
            bases=(models.Model, wagtail.search.index.Indexed),
        ),
    ]
