from django import forms
from django.apps import apps
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.db.models.fields import IntegerField
from django.utils import timezone
from library_website.settings.base import PHONE_FORMAT, PHONE_ERROR_MSG, POSTAL_CODE_FORMAT, POSTAL_CODE_ERROR_MSG, HOURS_TEMPLATE, HOURS_PAGE, ROOT_UNIT, LIBCAL_IID
from unidecode import unidecode
from wagtail.wagtailadmin.edit_handlers import TabbedInterface, ObjectList, FieldPanel, MultiFieldPanel, FieldRowPanel, PageChooserPanel, StreamFieldPanel
from wagtail.wagtailcore.blocks import ChoiceBlock, TextBlock, StructBlock, StreamBlock, FieldBlock, CharBlock, ListBlock, RichTextBlock, BooleanBlock, RawHTMLBlock, URLBlock, PageChooserBlock, TimeBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Page, Site
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailembeds.blocks import EmbedBlock 
from wagtail.wagtailsearch import index
from wagtail.wagtaildocs.models import Document
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from localflavor.us.us_states import STATE_CHOICES
from localflavor.us.models import USStateField
from base.utils import get_all_building_hours, get_hours_and_location, has_news_stories
from ask_a_librarian.utils import get_chat_status, get_chat_status_css, get_unit_chat_link
from wagtail.contrib.table_block.blocks import TableBlock
from django.utils import translation
from units.utils import get_default_unit

from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name
import json
import logging
import sys
import urllib

# Helper functions and constants
BUTTON_CHOICES = (
    ('btn-primary', 'Primary'),
    ('btn-default', 'Secondary'),
    ('btn-reserve', 'Reservation'),
)

def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Converts an integer to a base36 string."""
    if not isinstance(number, int):
        raise TypeError('number must be an integer')

    base36 = ''
    sign = ''

    if number < 0:
        sign = '-'
        number = -number

    if 0 <= number < len(alphabet):
        return sign + alphabet[number]

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return sign + base36

def base36decode(number):
    return int(number, 36)

# e.g. path "00010002" returns "000100020004", when "000100020003" is the highest path number that currently exists. 
def get_available_path_under(path):
    child_pages = filter(lambda p: p.path.startswith(path) and len(p.path) == len(path) + 4, apps.get_model('wagtailcore.Page').objects.all())
    child_paths = sorted(map(lambda c: c.path, child_pages))
    if child_paths:
        # strip off leading zeros from base 36 number: returns something like "Z"
        p = child_paths.pop()[-4:].lstrip("0")
        # turn it into an integer and add one to it.
        p = base36decode(p) + 1
        # turn it back to base 36 and pad the string with zeros so it's four characters long.
        p = base36encode(p).zfill(4)
        return "%s%s" % (path, p)
    else:
        return "%s0001" % path

def make_slug(s):
    s = unidecode(s)
    s = s.lower()
    s = ' '.join(s.split()) # replace multiple spaces with a single space.
    s = s.strip()
    s = s.replace('.', '')
    s = s.replace(',', '')
    s = s.replace('\'', '')
    s = s.replace('(', '')
    s = s.replace(')', '')
    s = s.replace('&', 'and')
    s = s.replace(' ', '-')
    s = s.replace('---', '-')
    return s

def get_breadcrumbs(page):
    breadcrumbs = list(map(lambda p: {'title': p.title, 'url': p.url}, page.get_ancestors(True)))
    # hack to remove the default root page.
    breadcrumbs.pop(0)
    return breadcrumbs

def recursively_add_children(page, current_site):
    """
    Recursively add child pages to a data structure
    that is a list of dictionaries. Used to create 
    a sitemap like index on pages.

    Args:
        page: object.

        current_site: site object
    """
    return {
        'title': page.title,
        'url': page.relative_url(current_site),
        'children': list(map(lambda p: recursively_add_children(p, current_site), page.get_children().live()))
    }


def get_index_html(currentlevel):
    """
    Generate html for a sitemap like index listing
    of child pages.  

    Args:
        currentlevel: list of dictionaries containing
        page information. 

    Returns:
        html, string
    """
    if not currentlevel:
        return ''
    else:
        return "<ul class='index-list'>" + "".join(list(map(lambda n: "<li><a href='" + n['url'] + "'>" + n['title'] + "</a>" + get_index_html(n['children']) + "</li>", currentlevel))) + "</ul>"


# Abstract classes
class Address(models.Model):
    """
    Reusable address fields.
    """
    address_1 = models.CharField(max_length=255, blank=True)
    address_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = USStateField(choices = STATE_CHOICES, default='IL')
    country = models.CharField(max_length=255, blank=True)
    postal_code_regex = RegexValidator(regex=POSTAL_CODE_FORMAT, message=POSTAL_CODE_ERROR_MSG)
    postal_code = models.CharField(validators=[postal_code_regex], max_length=5, blank=True)

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('address_1'),
                FieldPanel('address_2'),
                FieldPanel('city'),
                FieldPanel('state'),
                FieldPanel('postal_code'),
            ],
            heading='Address'
        ),
    ]

    class Meta:
        abstract = True


class Email(models.Model):
    """
    Reusable email address.
    """
    email_label = models.CharField(max_length=254, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    
    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('email_label'),
                FieldPanel('email'),
            ],
            heading='Email'
        ),
    ]

    class Meta:
        abstract = True


class PhoneNumber(models.Model):
    """
    Abstract phone number type.
    """
    phone_label = models.CharField(max_length=254, blank=True)
    phone_regex = RegexValidator(regex=PHONE_FORMAT, message=PHONE_ERROR_MSG)
    phone_number = models.CharField(validators=[phone_regex], max_length=12, blank=True)

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('phone_label'),
                FieldPanel('phone_number'),
            ],
            heading='Phone Number'
        ),
    ]

    class Meta:
        abstract = True


class FaxNumber(models.Model):
    """
    Abstract phone number type.
    """
    phone_regex = RegexValidator(regex=PHONE_FORMAT, message=PHONE_ERROR_MSG)
    fax_number = models.CharField(validators=[phone_regex], max_length=12, blank=True)

    content_panels = [
        FieldPanel('fax_number'),
    ]

    class Meta:
        abstract = True


class LinkFields(models.Model):
    """
    Reusable abstract class for general links.
    """
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    content_panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    class Meta:
        abstract = True


class LinkedText(LinkFields):
    """
    Generic link with text.
    """
    link_text = models.CharField(max_length=255, blank=True) 

    content_panels = [
        FieldPanel('link_text'),
    ] + LinkFields.content_panels
    
    class Meta:
        abstract = True


class ContactFields(Email, PhoneNumber, FaxNumber, LinkedText):
    """
    Reusable general contact fields.
    """

    content_panels = Email.content_panels + PhoneNumber.content_panels + FaxNumber.content_panels + LinkedText.content_panels

    class Meta:
        abstract = True


class SocialMediaFields(models.Model):
    """
    Social media links and buttons.
    """
    twitter_page = models.URLField(blank=True) 
    facebook_page = models.URLField(blank=True) 
    hashtag = models.CharField(max_length=45, blank=True) 
    hashtag_page = models.URLField(blank=True, \
        help_text='Link to twitter page using a hashtag')
    instagram_page = models.URLField(blank=True)
    youtube_page = models.URLField(blank=True)
    blog_page = models.URLField(blank=True)
    tumblr_page = models.URLField(blank=True)
    snapchat_page = models.URLField(blank=True)

    @property
    def has_social_media(self):
        if self.twitter_page:
            return True
        elif self.facebook_page:
            return True
        elif self.hashtag and self.hashtag_page:
            return True
        elif self.instagram_page or self.youtube_page or \
        self.blog_page or self.tumblr_page or self.snapchat_page:
            return True
        else:
            return False

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('twitter_page'),
                FieldPanel('facebook_page'),
                FieldPanel('hashtag'),
                FieldPanel('hashtag_page'),
                FieldPanel('instagram_page'),
                FieldPanel('youtube_page'),
                FieldPanel('blog_page'),
                FieldPanel('tumblr_page'),
                FieldPanel('snapchat_page'),
            ],
            heading='Social media'
        ),
    ]
 
    class Meta:
        abstract = True


class LinkedTextOrLogo(LinkedText):
    """
    Generic linked text or image/logo.
    """
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    @property
    def content(self):
        if self.logo:
            return self.logo
        elif self.link_text:
            return self.link_text
        else:
            return ''

    panels = [
        ImageChooserPanel('logo'),
    ] + LinkedText.content_panels
    
    class Meta:
        abstract = True


class AbstractButton(LinkFields):
    """
    Link with special styling and shorter 
    user editable text.
    """
    button_text = models.CharField(max_length=20, blank=False) 

    panels = [
        FieldPanel('button_text'),
    ] + LinkFields.content_panels
    
    class Meta:
        abstract = True


class Button(AbstractButton):
    """
    A simple button.
    """
    button_type = forms.ChoiceField(
        choices=BUTTON_CHOICES,
        initial='btn-primary'
    )

    panels = [
        FieldPanel('button_type'),
    ] + AbstractButton.panels

    class Meta:
        abstract = True


class AbstractReport(LinkFields):
    """
    Abstract base type for meeting minutes and reports.
    """
    date = models.DateField(blank=False)
    summary = models.TextField(null=False, blank=False)

    panels = [
        FieldPanel('date'),
        FieldPanel('summary'),
    ] + LinkFields.content_panels

    class Meta:
        abstract = True
        ordering = ['-date']


class Report(AbstractReport):
    """
    Model for group and unit reports
    """
    panels = AbstractReport.panels

    class Meta:
        abstract = True

class AbstractBase(models.Model):
    """
    General fields to add to all page types.
    """ 
    start_sidebar_from_here = models.BooleanField(default=False)

    show_sidebar = models.BooleanField(default=False)

    last_reviewed = models.DateField(
        'Last Reviewed', 
        null=True, 
        blank=True
    )

    page_maintainer = models.ForeignKey(
        'staff.StaffPage',
        null=True, 
        blank=False, 
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_maintainer'
    )

    editor = models.ForeignKey(
        'staff.StaffPage',
        null=True, 
        blank=False, 
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_editor'
    )

    # Searchable fields
    search_fields = [
        index.SearchField('description'),
    ]

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('page_maintainer'),
                FieldPanel('editor'),
                FieldPanel('last_reviewed', None),
            ],
            heading='Page Management'
        ),
    ]

    left_sidebar_panels = [
        MultiFieldPanel(
            [
                FieldPanel('start_sidebar_from_here'),
                FieldPanel('show_sidebar'),
            ],
            heading='Left Sidebar Menus'
        ),
    ]

    class Meta:
        abstract = True


# Global streamfield definitions
class ImageFormatChoiceBlock(FieldBlock):
    """
    Alignment options to use with the ImageBlock.
    """
    field = forms.ChoiceField(choices=(
        ('pull-left', 'Wrap left'), ('pull-right', 'Wrap right'), ('fullwidth', 'Full width'),
    ))

class ImageBlock(StructBlock):
    """
    Image streamfield block.
    """
    image = ImageChooserBlock()
    title = CharBlock(required=False)
    citation = CharBlock(
        required=False,
        help_text='Photographer, artist, or creator of image',
    )
    caption = TextBlock(
        required=False,
        help_text='Details about or description of image',
    )
    alt_text = CharBlock(
        required=False,
        help_text='Invisible text for screen readers',
    ) #Img title in the system is a fallback. 
    alignment = ImageFormatChoiceBlock()
    source = URLBlock(
        required=False,
        help_text='Link to image source (needed for Creative Commons)',
    )
    lightbox = BooleanBlock(
        default=False, 
        required=False,
        help_text='Link to a larger version of the image',
    )

    class Meta:
        icon = 'image'
        template ='base/blocks/img.html'

class BlockQuoteBlock(StructBlock):
    """
    Blockquote streamfield block.
    """
    quote = TextBlock('quote title')
    attribution = CharBlock(required=False)

    class Meta:
        icon = 'openquote'
        template = 'base/blocks/blockquote.html'


class ButtonBlock(StructBlock):
    """
    Button streamfield block.
    """
    button_type = ChoiceBlock(choices=BUTTON_CHOICES, default=BUTTON_CHOICES[0][0])
    button_text = CharBlock(max_length=20)
    link_external = URLBlock(required=False)
    link_page = PageChooserBlock(required=False)
    link_document = DocumentChooserBlock(required=False) 

    class Meta:
        icon = 'plus-inverse'
        template = 'base/blocks/button.html'


class ClearBlock(StructBlock):
    """
    Allows authors to add a clear between floated elements.
    """
    class Meta:
        icon = 'horizontalrule'
        template = 'base/blocks/clear.html'


class ParagraphBlock(StructBlock):
    """
    Paragraph streamfield block.
    """
    paragraph = RichTextBlock()

    class Meta:
        icon = 'pilcrow'
        form_classname = 'paragraph-block struct-block'
        template = 'base/blocks/paragraph.html'

class CodeBlock(StructBlock):
    """
    Code Highlighting Block
    """

    LANGUAGE_CHOICES = (
        ('bash', 'Bash/Shell'),
        ('css', 'CSS'),
        ('html', 'HTML'),
        ('javascript', 'Javascript'),
        ('json', 'JSON'),
        ('ocaml', 'OCaml'),
        ('php5', 'PHP'),
        ('html+php', 'PHP/HTML'),
        ('python', 'Python'),
        ('scss', 'SCSS'),
        ('yaml', 'YAML'),
    )

    language = ChoiceBlock(choices=LANGUAGE_CHOICES)
    code = TextBlock()

    class Meta:
        icon = 'cog'
        label = '_SRC'

    def render(self, value):
        src = value['code'].strip('\n')
        lang = value['language']

        lexer = get_lexer_by_name(lang)
        formatter = get_formatter_by_name(
            'html',
            linenos=None,
            cssclass='codehilite',
            style='default',
            noclasses=False,
        )
        return mark_safe(highlight(src, lexer, formatter))


class AgendaInnerBlock(StructBlock):
    """
    Block definition for the repeatable inner 
    portion of the AgendaItem streamfield.
    """
    title = CharBlock(required=False, 
        help_text='Talk title, workshop title, etc.')
    presenters = CharBlock(required=False,
        help_text='Comma separated list of presenters \
            (if more than one)')
    room_number = CharBlock(required=False)
    description = RichTextBlock(required=False)


class AgendaItemFields(StructBlock):
    """
    Make the AgendaInnerBlock repeatable.
    """
    start_time = TimeBlock(required=False, icon='time')
    end_time = TimeBlock(required=False, icon='time')
    session_title = CharBlock(required=False, 
        icon='title',
        help_text='Title of the session. \
            Can be used as title of the talk in some situations.')
    event = ListBlock(AgendaInnerBlock(), 
        icon="edit",
        help_text='A talk or event with a title, presenter \
            room number, and description',
        label=' ')


class LinkBlock(StructBlock):
    """
    Generic block for inserting links. This is duplicate code
    of LinkedText via LinkFields. I haven't figured out how 
    to extend StructBlock and LinkedText at the same time.
    """
    link_text = CharBlock(max_length=255, required=False)
    link_external = URLBlock(required=False)
    link_page = PageChooserBlock(required=False)


class DefaultBodyFields(StreamBlock):
    """
    Standard default streamfield options to be shared 
    across content types.
    """
    h2 = CharBlock(icon='title', classname='title', template='base/blocks/h2.html')
    h3 = CharBlock(icon='title', classname='title', template='base/blocks/h3.html')
    h4 = CharBlock(icon='title', classname='title', template='base/blocks/h4.html')
    h5 = CharBlock(icon='title', classname='title', template='base/blocks/h5.html')
    h6 = CharBlock(icon='title', classname='title', template='base/blocks/h6.html')
    paragraph = ParagraphBlock()
    image = ImageBlock(label='Image')
    blockquote = BlockQuoteBlock()
    button = ButtonBlock()
    video = EmbedBlock(icon='media')
    code = CodeBlock()
    agenda_item = AgendaItemFields(icon='date', template='base/blocks/agenda.html')
    clear = ClearBlock()

    # Begin TableBlock Setup
    language = translation.get_language()
    if language is not None and len(language) > 2:
        language = language[:2]

    options = {
        'minSpareRows': 0,
        'startRows': 3,
        'startCols': 3,
        'colHeaders': False,
        'rowHeaders': False,
        'contextMenu': True,
        'editor': 'text',
        'stretchH': 'all',
        'height': 108,
        'language': language,
        'renderer': 'html',
        'autoColumnSize': False,
    }
    table = TableBlock(
        table_options=options, 
        template='base/blocks/table.html', 
        help_text='Right + click in a table cell for more options. Use <em>text</em> for italics, \
<strong>text</strong> for bold, and <a href="https://duckduckgo.com">text</a> for links.',
    ) 


class RawHTMLBodyField(StreamBlock):
    """
    Streamfield for raw HTML.
    """
    html = RawHTMLBlock()


# Page definitions
class BasePage(Page, AbstractBase):
    """
    Adds additional fields to the wagtail Page model.
    Most other content types should extend this model
    instead of Page.
    """

    # Searchable fields
    search_fields = Page.search_fields + AbstractBase.search_fields

    content_panels = AbstractBase.content_panels
    left_sidebar_panels = AbstractBase.left_sidebar_panels
    promote_panels = Page.promote_panels + left_sidebar_panels

    class Meta:
        abstract = True

    def get_context(self, request):
        context = super(BasePage, self).get_context(request)

        context['breadcrumbs'] = get_breadcrumbs(self)

        context['sidebartitle'] = 'Browse this Section'
        if self.specific_class.get_verbose_name() == 'Intranet Units Page':
            for p in list(reversed(self.get_ancestors(True))):
                try:
                    if p.specific.start_sidebar_from_here:
                        context['sidebartitle'] = p.title
                        break
                except:
                    pass
                
        # JEJ- fix this later to remove logic from the template.
        current_site = Site.find_for_request(request)
        sidebar = [] 
        if self.show_sidebar:
            ancestors = self.get_ancestors(True).specific()
            a = len(ancestors) - 1
            while a > 0:
                sidebar_parent = ancestors[a]
                if sidebar_parent.start_sidebar_from_here:
                    break
                a = a - 1

            children = sidebar_parent.get_children().in_menu().live().specific()
            for child in children:
                new_child = {
                    'title': child.title,
                    'url': child.relative_url(current_site),
                    'children': []
                }
                grandchildren = child.get_children().in_menu().live().specific()
                for grandchild in grandchildren:
                    new_child['children'].append({
                        'title': grandchild.title,
                        'url': grandchild.relative_url(current_site),
                        'children': [],
                    })

                sidebar.append(new_child)
        context['sidebar'] = sidebar
        
        return context


class PublicBasePage(BasePage):
    """
    Adds additional fields to the wagtail Page model.
    Most other content types should extend this model
    instead of Page.
    """
    # Fields 
    #location = models.ForeignKey('public.LocationPage',  
    #    null=True, blank=True, on_delete=models.SET_NULL, limit_choices_to={'is_building': True},
    #    related_name='%(app_label)s_%(class)s_related')

    # Quicklinks fields
    quicklinks = RichTextField(blank=True)
    quicklinks_title = models.CharField(max_length=100, blank=True)
    view_more_link = models.URLField(max_length=255, blank=True, default='')
    view_more_link_label = models.CharField(max_length=100, blank=True)

    # Sidebar hours
    display_hours_in_right_sidebar = models.BooleanField(default=False)

    # Index fields 
    enable_index = models.BooleanField(default=False)
    display_hierarchical_listing = models.BooleanField(default=False)

    # Workshops and Events
    events_feed_url = models.URLField(blank=True, help_text='Link to a Tiny Tiny RSS Feed')

    # News
    news_feed_url = models.URLField(blank=True, help_text='Link to a WordPress Feed from the Library News Site') 
    active_tag =  models.CharField(max_length=30, blank=True, help_text='A WordPress tag name used for display purposes, e.g. "Library Kiosk"')

    unit = models.ForeignKey(
        'units.UnitPage', 
        null=True, 
        blank=False, 
        limit_choices_to={'display_in_dropdown': True},
        on_delete=models.SET_NULL, 
        related_name='%(app_label)s_%(class)s_related'
    )

    content_specialist = models.ForeignKey(
        'staff.StaffPage',
        null=True, 
        blank=False, 
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_content_specialist'
    )

    # Searchable fields
    search_fields = Page.search_fields + BasePage.search_fields 

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('page_maintainer'),
                FieldPanel('editor'),
                FieldPanel('content_specialist'),
                FieldPanel('unit'),
                FieldPanel('last_reviewed', None),
            ],
            heading='Page Management'
        ),
    ]

    left_sidebar_panels = BasePage.left_sidebar_panels
    promote_panels = BasePage.promote_panels

    class Meta:
        abstract = True


    def get_hours_page(self, request):
        """
        Get a link to the hours page from the ID set
        in the base config file.

        Args:
            request, object

        Return:
            String, url. 
        """
        try:
            current_site = Site.find_for_request(request)
            return Page.objects.all().filter(id=HOURS_PAGE)[0].relative_url(current_site)
        except(IndexError) as e:
            msg = 'HOURS_PAGE in settings.base is configured incorrectly. \
Either it is set to the ID of a non-existing page or it has an incorrect value.'
            raise IndexError(msg)


    def get_sidebar_title(self):
        """
        Recursively search up the tree to get the title and 
        url for a sidebar. The title and url returned will
        be the first ancestor with the start_sidebar_from_here
        parameter set. If nothing is found a tuple of empty
        strings is returned.

        Returns:
            Tuple where the first item is a page title and
            the second item is a page url. 
        """
        try:
            if self.start_sidebar_from_here:
                return (self.title, self.url)
            else:
                return self.get_parent().specific.get_sidebar_title()
        except:
            return ('', '')


    def has_left_sidebar(self, context):
        """
        Logic for determining is a left sidebar should
        be shown.
 
        Args:
            context: django context dictionary

        Returns:
            Boolean
        """
        return bool(self.show_sidebar and context['sidebar'])


    def get_conditional_css_classes(self, divname, sidebar):
        """
        Get css classes for the main content div and    
        breadcrumbs depending on whether or not a 
        left sidebar is needed.

        Args:
            divname: string, the arbitrary name of a div

            sidebar: boolean

        Returns:
            String, list of css classes to be applied
            to a div.
        """
        css = {'breadcrumbs': {True: 'col-md-10 breadcrumbs hidden-xs hidden-sm', False: 'col-md-12 breadcrumbs hidden-xs hidden-sm'},
               'content': {True: 'container body-container col-xs-12 col-md-10', False: 'container body-container col-xs-12 col-lg-11 col-lg-offset-1'}}
        return css[divname][sidebar]


    def get_branch_lib_css_class(self):
        """
        Get the css classes for fancy pages and 
        subsections of the site based on location.

        Returns:
            String, css classname.
        """
        # TODO: move this to base.settings and use page ID instead of page title
        css = { 'The John Crerar Library' : 'crerar',
                'The D\'Angelo Law Library': 'law',
                'Eckhart Library': 'eckhart',
                'The Joe and Rika Mansueto Library': 'mansueto',
                'The Joseph Regenstein Library': 'reg',
                'Social Service Administration Library': 'ssa'}
        try:
            key = str(get_hours_and_location(self)['page_location'])
            return css[key]
        except(KeyError):
            return ''

    def get_granular_libcal_lid(self, unit):
        """
        Get the most specific libcal library ID
        for the display of the most granular hours. 
        Recurrs up the tree visiting all parent pages
        and looks at unit -> location -> libcal_library_id
        assignments and returnts the first one found.
        If a granular libcal ID isn't found, display
        the default (Regenstein).
        
        Args:
            unit, page object.

        Returns:
            Integer 
        """
        try:
            current_page_id = unit.location.libcal_library_id
            if current_page_id:
                return current_page_id
            else: 
                return self.get_granular_libcal_lid(self.get_parent().unit.location)
        except(AttributeError):
            return get_default_unit().location.libcal_library_id 
      

    def has_granular_hours(self):
        """
        Check to see if granular hours should be 
        displayed in the right sidebar.

        Returns:
            Boolean
        """
        try:
            is_building = self.is_building
        except(AttributeError):
            is_building = False
        return True if is_building or self.has_field([self.display_hours_in_right_sidebar]) else False


    def has_field(self, field_list):
        """
        Helper method for checking the page object
        to see if specific fields are filled out.
        Returns True if any one field is present
        in the list. Note: actually checks
        values in practice.

        Args:
            field_list: list of page field objects.

        Returns:
            Boolean
        """
        for field in field_list:
            if field:
                return True
        return False


    def base_has_right_sidebar(self):
        """
        Determine if a right sidebar should
        be displayed in the template.

        Returns:
            boolean
        """
        fields = [self.quicklinks, self.events_feed_url]
        return self.has_field(fields) or self.has_granular_hours()


    def get_banner(self, current_site):
        """
        Test to see if a page should have a banner image. 
        Get the image url for display if the anser is yes.

        Args:
            current_site: site object.

        Returns:
            A tuple where the first value is a boolean, 
            the second value is an image object or None, 
            the third value is a string (banner title),
            and the fourth value is a link.
        """
        try:
            # Base case
            if self.banner_title and self.banner_image:
                return (True, self.banner_image, self.banner_title, self.relative_url(current_site))
            # Recursive case
            else:
                return self.get_parent().specific.get_banner(current_site)
        # Reached the top of the tree (could factor this into an if)
        except(AttributeError):
            return (False, None, '', '')


    def get_context(self, request):
        context = super(PublicBasePage, self).get_context(request)
        location_and_hours = get_hours_and_location(self)
        unit = location_and_hours['page_unit']     
        current_site = Site.find_for_request(request)
        url_filter = '~()*!.\''

        try: 
            location = str(location_and_hours['page_location'])
            context['page_unit'] = str(unit) 
            context['page_location'] = location
            #context['current_building_hours'] = location_and_hours['hours']
            context['address'] = location_and_hours['address']
            #context['all_building_hours'] = get_all_building_hours()
            context['chat_url'] = get_unit_chat_link(unit, request)
            context['directory_link'] = self.get_directory_link_by_location(location)
        except(AttributeError):
            logger = logging.getLogger(__name__)
            logger.error('Context variables not set in PublicBasePage.')

        context['libcalid'] = location_and_hours['libcalid']
        context['granular_libcalid'] = self.get_granular_libcal_lid(self.unit)
        context['libcaliid'] = LIBCAL_IID
        context['has_granular_hours'] = self.has_granular_hours()
        context['all_spaces_link'], \
        context['quiet_spaces_link'], \
        context['collaborative_spaces_link'] = self.get_spaces_links(location_and_hours)
        context['chat_status'] = get_chat_status('uofc-ask')
        context['chat_status_css'] = get_chat_status_css('uofc-ask')

        sidebar = self.has_left_sidebar(context)
        context['has_left_sidebar'] = sidebar
        context['content_div_css'] = self.get_conditional_css_classes('content', sidebar)
        context['breadcrumb_div_css'] = self.get_conditional_css_classes('breadcrumbs', sidebar)
        context['sidebartitle'] = self.get_sidebar_title()[0]
        context['sidebartitleurl'] = self.get_sidebar_title()[1]
        context['branch_lib_css'] = self.get_branch_lib_css_class()
        context['hours_page_url'] = self.get_hours_page(request)
        context['is_hours_page'] = self.id == HOURS_PAGE
        context['has_banner'] = self.get_banner(current_site)[0]
        context['banner'] = self.get_banner(current_site)[1]
        context['banner_title'] = self.get_banner(current_site)[2]
        context['banner_url'] = self.get_banner(current_site)[3]
        context['page_type'] = str(self.specific.__class__.__name__)
        context['events_feed'] = urllib.parse.quote(self.events_feed_url, safe=url_filter)
        context['news_feed'] = urllib.parse.quote(self.news_feed_url, safe=url_filter)
        context['active_tag'] = urllib.parse.quote(self.active_tag)
        context['has_news_stories'] = has_news_stories(self.news_feed_url, self.active_tag)

        # Data structure for generating a 
        # sitemap display of child pages
        index_pages = [{
            'title': self.title,
            'url': self.relative_url(current_site),
            'children': [],
        }]

        # Build sitemap listing of child pages 
        # in html format.
        if self.enable_index and self.display_hierarchical_listing:
            index_pages[0]['children'] = list(map(lambda p: recursively_add_children(p, current_site), self.get_children().live()))
        elif self.enable_index:
            index_pages[0]['children'] = list(map(lambda p: {'title': p.title, 'url': p.relative_url(current_site), 'children': []}, self.get_children().live()))
        index_pages_html = get_index_html(index_pages[0]['children'])
        context['index_pages_html'] = index_pages_html

        return context

    def get_spaces_links(self, data):
        """
        Get the all the links for the find spaces module.
        Includes a link to the quiet study, collaborative 
        study, and unfilterd location browses. These 
        are filtered by building when appropriate.
        
        Args:
            data: mixed dictionary or objects and strings
            created by base.utils.get_hours_and_location.

        Returns:
            List of strings. These are links into the
            locations browse with filtered by building,
            and feature as needed. Links are ordered in
            the list like this:

            1. All spaces link 
            2. Quiet spaces link 
            3. Collaborative spaces link
        """
        base_url = '/spaces/'

        if self.unit.id == ROOT_UNIT:
            all_spaces = base_url 
            quiet_spaces = '%s?%s' % (base_url, urllib.parse.urlencode({'feature': 'is_quiet_zone'}))
            collaborative_spaces = '%s?%s' % (base_url, urllib.parse.urlencode({'feature': 'is_collaborative_zone'}))
        else:
            all_spaces = '%s?%s' % (base_url, urllib.parse.urlencode({'building': str(data['page_location'])}))
            quiet_spaces = '%s?%s' % (base_url, urllib.parse.urlencode({'building': str(data['page_location']), 'feature': 'is_quiet_zone'}))
            collaborative_spaces = '%s?%s' % (base_url, urllib.parse.urlencode({'building': str(data['page_location']), 'feature': 'is_collaborative_zone'}))
        return [all_spaces, quiet_spaces, collaborative_spaces]

    @property
    def friendly_name(self):
        """
        Get the friendly name of the unit associated 
        with any given page. If the unit doesn't have 
        one, return an empty string.

        Returns:
            string, friendly name of assocaited unit
            with an extra space appended or an empty
            string if no friendly name is found.
        """
        try:
            return self.unit.friendly_name + ' '
        except(AttributeError):
            return ''

class IntranetPlainPage(BasePage):
    body = StreamField(DefaultBodyFields())

    subpage_types = ['base.IntranetIndexPage', 'base.IntranetPlainPage', 'intranettocs.TOCPage']

    search_fields = BasePage.search_fields + [
        index.SearchField('body'),
    ]

IntranetPlainPage.content_panels = Page.content_panels + [
    StreamFieldPanel('body')
] + BasePage.content_panels


class IntranetIndexPage(BasePage):
    intro = StreamField(DefaultBodyFields())
    display_hierarchical_listing = models.BooleanField(default=False)
    body = StreamField(DefaultBodyFields())

    subpage_types = ['base.IntranetIndexPage', 'base.IntranetPlainPage', 'intranettocs.TOCPage']

    content_panels = Page.content_panels + [
        StreamFieldPanel('intro'),
        FieldPanel('display_hierarchical_listing'),
        StreamFieldPanel('body')
    ] + BasePage.content_panels

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    def get_context(self, request):
        context = super(IntranetIndexPage, self).get_context(request)

        pages = [{
            'title': self.title,
            'url': self.url,
            'children': [],
        }]

        if self.display_hierarchical_listing:
            def recursively_add_children(page):
                return {
                    'title': page.title,
                    'url': page.url,
                    'children': list(map(lambda p: recursively_add_children(p), page.get_children().live()))
                }
            pages[0]['children'] = list(map(lambda p: recursively_add_children(p), self.get_children().live()))
                
        else:
            pages[0]['children'] = list(map(lambda p: {'title': p.title, 'url': p.url, 'children': []}, self.get_children().live()))

        def alphabetize_pages(currentlevel):
            for node in currentlevel:
                node['children'] = alphabetize_pages(node['children'])
            return sorted(currentlevel, key=lambda c: c['title'])
        pages = alphabetize_pages(pages)

        def get_html(currentlevel):
            if not currentlevel:
                return ''
            else:
                return "<ul class='index-list'>" + "".join(list(map(lambda n: "<li><a href='" + n['url'] + "'>" + n['title'] + "</a>" + get_html(n['children']) + "</li>", currentlevel))) + "</ul>"
        pages_html = get_html(pages[0]['children'])
        
        context['pages_html'] = pages_html

        context['pages'] = pages[0]['children']
        context['pages_html'] = pages_html
        return context


