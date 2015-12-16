from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.db.models.fields import BooleanField, CharField, TextField
from base.models import BasePage, DefaultBodyFields
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtaildocs.models import Document
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from modelcluster.fields import ParentalKey
from subjects.models import Subject
from base.models import PhoneNumber, Email

class StaffPageSubjectPlacement(Orderable, models.Model):
    """
    Through table for linking Subject snippets to StaffPages.
    """
    page = ParentalKey('staff.StaffPage', related_name='staff_subject_placements')
    subject = models.ForeignKey('subjects.Subject', related_name='+')

    class Meta:
        verbose_name = 'Subject Placement'
        verbose_name_plural = 'Subject Placements'

    panels = [
        SnippetChooserPanel('subject'),
    ]

    def __str__(self):
        return self.page.title + ' -> ' + self.subject.name


class VCard(Email, PhoneNumber):
    """
    VCard model for repeatable VCards on the 
    StaffPage.
    """
    title = CharField(
        max_length=255, 
        blank=False)
    unit = models.ForeignKey(
       'directory_unit.DirectoryUnit',
       null=True,
       blank=True,
       on_delete=models.SET_NULL,
       related_name='%(app_label)s_%(class)s_related'
    )
    faculty_exchange = CharField(
        max_length=255, 
        blank=True)

    content_panels = [
        FieldPanel('title'),
        FieldPanel('unit'),
        FieldPanel('faculty_exchange'),
    ]


class StaffPagePageVCards(Orderable, VCard):
    """
    Create a through table for linking vcards
    to StaffPage content types.
    """
    page = ParentalKey('staff.StaffPage', related_name='vcards')


class StaffPageManager(models.Manager):
    def get_query_set(self):
        return (
            super(StaffPageManager, self)
            .get_query_set()
            .order_by('title')
        )


class StaffPage(BasePage):
    """
    Staff profile content type.
    """
    cnetid = CharField(
        max_length=255,
        blank=False)
    display_name = CharField(
        max_length=255,
        null=True,
        blank=True)
    official_name = CharField(
        max_length=255,
        null=True,
        blank=True)
    first_name = CharField(
        max_length=255,
        null=True,
        blank=True)
    middle_name = CharField(
        max_length=255,
        null=True,
        blank=True)
    last_name = CharField(
        max_length=255,
        null=True,
        blank=True)
    supervisor = models.ForeignKey(
        'staff.StaffPage',
        null=True, blank=True, on_delete=models.SET_NULL)
    profile_picture = models.ForeignKey(
                'wagtailimages.Image',
                null=True,
                blank=True,
                on_delete=models.SET_NULL,
                related_name='+')
    libguide_url = models.URLField(
        max_length=255, 
        null=True, 
        blank=True)
    bio = StreamField(DefaultBodyFields(), blank=True, null=True)
    cv = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    is_public_persona = BooleanField(default=False)

    @property
    def get_staff_subjects(self):
        """
        Get the subjects beloning to the 
        staff member - UNTESTED 
        """
        return StaffPageSubjectPlacement.objects

    @property
    def is_subject_specialist(self):
        """
        See if the staff member is a subject
        specialist - PLACEHOLDER
        """
        subjects = self.get_subjects()
        return None

    objects = StaffPageManager

    content_panels = Page.content_panels + [
        FieldPanel('cnetid'),
        MultiFieldPanel(
            [
                FieldPanel('official_name'),
                FieldPanel('display_name'),
                FieldPanel('first_name'),
                FieldPanel('middle_name'),
                FieldPanel('last_name'),
            ],
            heading='Name'
        ),
        FieldPanel('supervisor'),
        FieldPanel('libguide_url'),
        ImageChooserPanel('profile_picture'),
        StreamFieldPanel('bio'),
        DocumentChooserPanel('cv'),
        FieldPanel('is_public_persona'),
        InlinePanel('staff_subject_placements', label='Subject Specialties'),
        InlinePanel('vcards', label='VCards'),
    ] + BasePage.content_panels

    subpage_types = ['base.IntranetPlainPage']

    class Meta:
        ordering = ['title']

class StaffIndexPage(BasePage):
    """
    Staff index page content type.
    """
    intro = RichTextField()
    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ] + BasePage.content_panels

    search_fields = Page.search_fields + ( # Inherit search_fields from Page
        index.SearchField('intro'),
    )

    subpage_types = ['base.IntranetPlainPage', 'staff.StaffPage']

    def get_context(self, request):
        staff_pages = []
        for s in StaffPage.objects.live():
            staff_pages.append({
            'title': s.title,
            'url': s.url
        })

        context = super(StaffIndexPage, self).get_context(request)
        context['staff_pages'] = staff_pages
        return context
