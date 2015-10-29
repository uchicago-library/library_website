from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.db.models.fields import BooleanField, CharField, TextField

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
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
        'units.UnitPage',
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


class StaffPage(Page):
    cnetid = CharField(
        max_length=255,
        null=True,
        blank=True)
    profile_picture = models.ForeignKey(
                'wagtailimages.Image',
                null=True,
                blank=True,
                on_delete=models.SET_NULL,
                related_name='+')
    official_name = CharField(
        max_length=255,
        null=True,
        blank=True)
    display_name = CharField(
        max_length=255,
        null=True,
        blank=True)
    alphabetize_name_as = CharField(
        max_length=255,
        null=True,
        blank=True)
    #supervisor = pointer to another staff person.
    libguide_url = CharField(
        max_length = 255,
        null=True,
        blank=True)
    bio = TextField(
        null=True,
        blank=True)
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


    content_panels = Page.content_panels + [
        ImageChooserPanel('profile_picture'),
        FieldPanel('alphabetize_name_as'),
        FieldPanel('bio'),
        DocumentChooserPanel('cv'),
        FieldPanel('is_public_persona'),
        InlinePanel('staff_subject_placements', label='Subject Specialties'),
        InlinePanel('vcards', label='VCards'),
    ]

class StaffIndexPage(Page):
    intro = TextField()
    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    search_fields = Page.search_fields + ( # Inherit search_fields from Page
        index.SearchField('intro'),
    )

    subpage_types = ['staff.StaffPage']
