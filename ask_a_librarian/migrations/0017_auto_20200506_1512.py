# Generated by Django 3.0.6 on 2020-05-06 20:12

import base.models
from django.db import migrations
import wagtail.contrib.table_block.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.images.blocks
import wagtail.snippets.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('ask_a_librarian', '0016_auto_20200308_0541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='askpage',
            name='body',
            field=wagtail.core.fields.StreamField([('h2', wagtail.core.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h2.html')), ('h3', wagtail.core.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h3.html')), ('h4', wagtail.core.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h4.html')), ('h5', wagtail.core.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h5.html')), ('h6', wagtail.core.blocks.CharBlock(classname='title', icon='title', template='base/blocks/h6.html')), ('paragraph', wagtail.core.blocks.StructBlock([('paragraph', wagtail.core.blocks.RichTextBlock())])), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('title', wagtail.core.blocks.CharBlock(required=False)), ('citation', wagtail.core.blocks.CharBlock(help_text='Photographer, artist, or creator of image', required=False)), ('caption', wagtail.core.blocks.TextBlock(help_text='Details about or description of image', required=False)), ('alt_text', wagtail.core.blocks.CharBlock(help_text='Invisible text for screen readers', required=False)), ('alignment', base.models.ImageFormatChoiceBlock()), ('source', wagtail.core.blocks.URLBlock(help_text='Link to image source (needed for Creative Commons)', required=False)), ('lightbox', wagtail.core.blocks.BooleanBlock(default=False, help_text='Link to a larger version of the image', required=False))], label='Image')), ('blockquote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.TextBlock('quote title')), ('attribution', wagtail.core.blocks.CharBlock(required=False))])), ('pullquote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock())])), ('button', wagtail.core.blocks.StructBlock([('button_type', wagtail.core.blocks.ChoiceBlock(choices=[('btn-primary', 'Primary'), ('btn-default', 'Secondary'), ('btn-reserve', 'Reservation')])), ('button_text', wagtail.core.blocks.CharBlock(max_length=20)), ('link_external', wagtail.core.blocks.URLBlock(required=False)), ('link_page', wagtail.core.blocks.PageChooserBlock(required=False)), ('link_document', wagtail.documents.blocks.DocumentChooserBlock(required=False))])), ('video', wagtail.embeds.blocks.EmbedBlock(icon='media')), ('code', wagtail.core.blocks.StructBlock([('language', wagtail.core.blocks.ChoiceBlock(choices=[('bash', 'Bash/Shell'), ('css', 'CSS'), ('html', 'HTML'), ('javascript', 'Javascript'), ('json', 'JSON'), ('ocaml', 'OCaml'), ('php5', 'PHP'), ('html+php', 'PHP/HTML'), ('python', 'Python'), ('scss', 'SCSS'), ('yaml', 'YAML')])), ('code', wagtail.core.blocks.TextBlock())])), ('agenda_item', wagtail.core.blocks.StructBlock([('start_time', wagtail.core.blocks.TimeBlock(icon='time', required=False)), ('end_time', wagtail.core.blocks.TimeBlock(icon='time', required=False)), ('session_title', wagtail.core.blocks.CharBlock(help_text='Title of the session.             Can be used as title of the talk in some situations.', icon='title', required=False)), ('event', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='Talk title, workshop title, etc.', required=False)), ('presenters', wagtail.core.blocks.CharBlock(help_text='Comma separated list of presenters             (if more than one)', required=False)), ('room_number', wagtail.core.blocks.CharBlock(required=False)), ('description', wagtail.core.blocks.RichTextBlock(required=False))]), help_text='A talk or event with a title, presenter             room number, and description', icon='edit', label=' '))], icon='date', template='base/blocks/agenda.html')), ('reusable_content', wagtail.core.blocks.StructBlock([('content', wagtail.snippets.blocks.SnippetChooserBlock('reusable_content.ReusableContent'))])), ('anchor_target', wagtail.core.blocks.StructBlock([('anchor_id_name', wagtail.core.blocks.CharBlock(max_length=50))], help_text='Where you want an anchor link to jump to. Must exactly match the "#" label supplied in anchor link (found in Paragraph streamfield).')), ('clear', wagtail.core.blocks.StructBlock([])), ('table', wagtail.contrib.table_block.blocks.TableBlock(help_text='Right + click in a table cell for more options. Use <em>text</em> for italics, <strong>text</strong> for bold, and <a href="https://duckduckgo.com">text</a> for links.', table_options={'autoColumnSize': False, 'colHeaders': False, 'editor': 'text', 'height': 108, 'language': 'en', 'minSpareRows': 0, 'renderer': 'html', 'rowHeaders': False, 'startCols': 3, 'startRows': 3, 'stretchH': 'all'}, template='base/blocks/table.html')), ('staff_listing', wagtail.core.blocks.StructBlock([('staff_listing', wagtail.core.blocks.ListBlock(wagtail.core.blocks.PageChooserBlock(), help_text='Be sure to select staff pages from Loop.', icon='edit', label='Staff listing')), ('show_photos', wagtail.core.blocks.BooleanBlock(default=False, help_text='Show staff photographs.', required=False)), ('show_contact_info', wagtail.core.blocks.BooleanBlock(default=False, help_text='Show contact information.', required=False)), ('show_subject_specialties', wagtail.core.blocks.BooleanBlock(default=False, help_text='Show subject specialties.', required=False))], icon='group', template='base/blocks/staff_listing.html')), ('solo_image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('citation', wagtail.core.blocks.RichTextBlock(blank=True, null=True)), ('caption', wagtail.core.blocks.RichTextBlock(blank=True, null=True, required=False)), ('alt_text', wagtail.core.blocks.CharBlock(help_text='Invisible text for screen readers', required=False))], help_text='Single image with caption on the right')), ('duo_image', wagtail.core.blocks.StructBlock([('image_one', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('citation', wagtail.core.blocks.RichTextBlock(blank=True, null=True)), ('caption', wagtail.core.blocks.RichTextBlock(blank=True, null=True, required=False)), ('alt_text', wagtail.core.blocks.CharBlock(help_text='Invisible text for screen readers', required=False))], help_text='First of two images displayed             side by side')), ('image_two', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('citation', wagtail.core.blocks.RichTextBlock(blank=True, null=True)), ('caption', wagtail.core.blocks.RichTextBlock(blank=True, null=True, required=False)), ('alt_text', wagtail.core.blocks.CharBlock(help_text='Invisible text for screen readers', required=False))], help_text='Second of two images displayed             side by side'))], help_text='Two images stacked side by side')), ('image_link', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('alt_text', wagtail.core.blocks.CharBlock(help_text='Invisible text for screen readers', required=False)), ('icon', wagtail.core.blocks.CharBlock(help_text="Font Awesome icon name if you're not using an image", required=False)), ('link_text', wagtail.core.blocks.CharBlock(help_text='Text to display below the image or icon', required=False)), ('link_external', wagtail.core.blocks.URLBlock(required=False)), ('link_page', wagtail.core.blocks.PageChooserBlock(required=False)), ('link_document', wagtail.documents.blocks.DocumentChooserBlock(required=False))], help_text='A fancy link made out of a thumbnail and simple text')), ('local_media', base.models.LocalMediaBlock(help_text='Audio or video files that are locally hosted')), ('html', wagtail.core.blocks.RawHTMLBlock())]),
        ),
    ]