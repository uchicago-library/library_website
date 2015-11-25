from django import forms
from django.apps import apps
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.fields import IntegerField
from django.utils import timezone
from library_website.settings.base import PHONE_FORMAT, PHONE_ERROR_MSG, POSTAL_CODE_FORMAT, POSTAL_CODE_ERROR_MSG
from unidecode import unidecode
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, FieldRowPanel, StreamFieldPanel
from wagtail.wagtailcore.blocks import TextBlock, StructBlock, StreamBlock, FieldBlock, CharBlock, ListBlock, RichTextBlock, RawHTMLBlock
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.blocks import ImageChooserBlock 
from wagtail.wagtailsearch import index

# e.g. path "00010002" returns "000100020004", when "000100020003" is the highest path number that currently exists. 
def get_available_path_under(path):
    child_pages = filter(lambda p: p.path.startswith(path) and len(p.path) == len(path) + 4, apps.get_model('wagtailcore.Page').objects.all())
    child_paths = sorted(map(lambda c: c.path, child_pages))
    if child_paths:
        return "%s%04d" % (path, int(child_paths.pop()[-4:]) + 1)
    else:
        return "%s0001" % path

def make_slug(s):
    s = unidecode(s)
    s = s.lower()
    s = ' '.join(s.split()) # replace multiple spaces with a single space.
    s = s.strip()
    s = s.replace('.', '')
    s = s.replace('\'', '')
    s = s.replace(' ', '-')
    return s

class BasePage(Page):
    """
    Adds additional fields to the wagtail Page model.
    Most other content types should extend this model
    instead of Page.
    """
    # Fields 
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

    sort_order = IntegerField(blank=True, default=0)

    # Searchable fields
    search_fields = Page.search_fields + (
        index.SearchField('description'),
    )

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('page_maintainer'),
                FieldPanel('editor'),
                FieldPanel('last_reviewed', None),
                FieldPanel('sort_order')
            ],
            heading='Page Management'
        ),
    ]

    class Meta:
        abstract = True

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

    unit = models.ForeignKey(
        'units.UnitPage', 
        null=True, 
        blank=True, 
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
    search_fields = Page.search_fields + (
        index.SearchField('description'),
    )

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

    class Meta:
        abstract = True

# Global streamfield definitions
class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'), ('center', 'Center'), ('full', 'Full width'),
    ))

class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = TextBlock(required=False)
    citation = CharBlock(required=False)
    alt_text = CharBlock(required=False) #Img title in the system is a fallback. 
    alignment = ImageFormatChoiceBlock()

    class Meta:
        icon = 'image'
        template ='base/blocks/img.html'

class BlockQuoteBlock(StructBlock):
    quote = TextBlock('quote title')
    attribution = CharBlock()

    class Meta:
        icon = 'openquote'
        template = 'base/blocks/blockquote.html'

class ParagraphBlock(StructBlock):
    paragraph = RichTextBlock()

    class Meta:
        icon = 'pilcrow'
        form_classname = 'paragraph-block struct-block'
        template = 'base/blocks/paragraph.html'

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
    #ordered_list = ListBlock(RichTextBlock(), icon="list-ol")
    #unordered_list = ListBlock(RichTextBlock(), icon="list-ul")

class DefaultBodyField(StreamField):
    """
    We need to get rid of this! Don't use this! 
    """
    def __init__(self, block_types=None, **kwargs):
        block_types = [
            ('heading', CharBlock(classname='full title', icon='title')),
            ('paragraph', RichTextBlock(icon='pilcrow')),
            ('image', ImageChooserBlock(icon='image / picture')),
        ]

        super(DefaultBodyField, self).__init__(block_types, **kwargs)

class IntranetPlainPage(BasePage):
    body = StreamField(DefaultBodyFields())

    subpage_types = ['base.IntranetPlainPage', 'base.IntranetSidebarPage']

IntranetPlainPage.content_panels = Page.content_panels + [
    StreamFieldPanel('body')
] + BasePage.content_panels

class IntranetSidebarPage(BasePage):
    body = StreamField(DefaultBodyFields())

    subpage_types = ['base.IntranetPlainPage', 'base.IntranetSidebarPage']

IntranetSidebarPage.content_panels = Page.content_panels + [
    StreamFieldPanel('body')
] + BasePage.content_panels

class Address(models.Model):
    """
    Reusable address fields.
    """
    address_1 = models.CharField(max_length=255, blank=True)
    address_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    postal_code_regex = RegexValidator(regex=POSTAL_CODE_FORMAT, message=POSTAL_CODE_ERROR_MSG)
    postal_code = models.CharField(validators=[postal_code_regex], max_length=5, blank=True)

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('address_1'),
                FieldPanel('address_2'),
                FieldPanel('city'),
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
    email = models.EmailField(max_length=254, blank=True)
    
    content_panels = [
        FieldPanel('email'),
    ]

    class Meta:
        abstract = True


class PhoneNumber(models.Model):
    """
    Abstract phone number type.
    """
    phone_label = models.CharField(max_length=25, blank=True)
    phone_regex = RegexValidator(regex=PHONE_FORMAT, message=PHONE_ERROR_MSG)
    phone_number = models.CharField(validators=[phone_regex], max_length=12, blank=True)

    content_panels = [
        FieldPanel('phone_label'),
        FieldPanel('phone_number'),
    ]

    class Meta:
        abstract = True


class FaxNumber(models.Model):
    """
    Abstract phone number type.
    """
    phone_regex = RegexValidator(regex=PHONE_FORMAT, message=PHONE_ERROR_MSG)
    fax_number = models.CharField(validators=[phone_regex], max_length=12, blank=True)

    panels = [
        FieldPanel('number'),
    ]

    class Meta:
        abstract = True


class Report(models.Model):
    """
    Model for group and unit reports
    """
    date = models.DateField(blank=False)
    summary = models.TextField(null=False, blank=False)
    link = models.URLField(max_length=254, blank=False, default='')

    panels = [
        FieldPanel('date'),
        FieldPanel('summary'),
        FieldPanel('link'),
    ]

    class Meta:
        abstract = True 
