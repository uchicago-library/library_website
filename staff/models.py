from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.db.models.fields import BooleanField, CharField, TextField
from base.models import BasePage, BasePageWithoutStaffPageForeignKeys, DefaultBodyFields
from library_website.settings.base import ORCID_FORMAT, ORCID_ERROR_MSG
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Orderable, Page, PageManager
from wagtail.wagtaildocs.models import Document
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailsnippets.models import register_snippet
from modelcluster.fields import ParentalKey
from subjects.models import Subject
from base.models import PhoneNumber, Email
import json, re

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

class StaffPageManager(PageManager):
    def get_queryset(self):
        return (
            super(StaffPageManager, self)
            .get_queryset()
            .order_by('last_name', 'first_name')
        )

class StaffPage(BasePageWithoutStaffPageForeignKeys):
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
    orcid_regex = RegexValidator(regex=ORCID_FORMAT, message=ORCID_ERROR_MSG)
    orcid = CharField(
        max_length=255,
        null=True,
        blank=True,
        validators=[orcid_regex]
    )

    objects = StaffPageManager()

    @property
    def get_staff_subjects(self):
        """
        Get the subjects beloning to the 
        staff member - UNTESTED 
        """
        return get_public_profile('elong')

    @property
    def is_subject_specialist(self):
        """
        See if the staff member is a subject
        specialist - PLACEHOLDER
        """
        subjects = self.get_subjects()
        return None

    @property
    def public_page(self):
        """
        Get a public staff profile page for the
        library expert if one exists.
        """
        from public.models import StaffPublicPage # Should try to do better
        try:
            return StaffPublicPage.objects.live().filter(title=self.cnetid)[0]
        except(IndexError):
            return None

    content_panels = Page.content_panels + [
        ImageChooserPanel('profile_picture'),
        StreamFieldPanel('bio'),
        DocumentChooserPanel('cv'),
        FieldPanel('libguide_url'),
        FieldPanel('is_public_persona'),
        InlinePanel('staff_subject_placements', label='Subject Specialties'),
        InlinePanel('expertise_placements', label='Expertise'),
        FieldPanel('orcid')
    ] + BasePageWithoutStaffPageForeignKeys.content_panels

    search_fields = BasePageWithoutStaffPageForeignKeys.search_fields + [
        index.SearchField('profile_picture'),
        index.SearchField('cv'),
        index.SearchField('libguide_url'),
        index.SearchField('orcid'),
        index.SearchField('staff_subject_placements')
    ]

    subpage_types = ['base.IntranetIndexPage', 'base.IntranetPlainPage', 'intranetforms.IntranetFormPage', 'intranettocs.TOCPage']

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_context(self, request):
        vcard_titles = set()
        faculty_exchanges = set()
        emails = set()
        phones = set()
        units = set()
    
        for vcard in self.vcards.all():
            vcard_titles.add(re.sub('\s+', ' ', vcard.title).strip())
            faculty_exchanges.add(re.sub('\s+', ' ', vcard.faculty_exchange).strip())
            emails.add(vcard.email)
            phones.add(vcard.phone_number)

            try:
                unit_title = vcard.unit.fullName
            except:
                unit_title = None
            try:
                unit_url = vcard.unit.intranet_unit_page.first().url
            except:
                unit_url = None
            units.add(json.dumps({
                'title': unit_title,
                'url': unit_url
            }))

        vcard_titles = list(vcard_titles)
        faculty_exchanges = list(faculty_exchanges)
        emails = list(emails)
        phones = list(phones)
        units = list(map(json.loads, list(units)))

        subjects = []
        for subject in self.staff_subject_placements.all():
            subjects.append({
                'name': subject.subject.name,
                'url': ''
            })

        group_memberships = []
        for group_membership in self.member.all():
            if group_membership.parent.is_active:
                group_memberships.append({
                    'group': {
                        'title': group_membership.parent.title,
                        'url': group_membership.parent.url
                    },
                    'role': group_membership.role
                })
            
        context = super(StaffPage, self).get_context(request)
        context['vcard_titles'] = vcard_titles
        context['faculty_exchanges'] = faculty_exchanges
        context['emails'] = emails
        context['phones'] = phones
        context['units'] = units
        context['subjects'] = subjects
        context['group_memberships'] = group_memberships
        return context

class StaffIndexPage(BasePage):
    """
    Staff index page content type.
    """
    intro = RichTextField()
    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ] + BasePage.content_panels

    search_fields = Page.search_fields + [ # Inherit search_fields from Page
        index.SearchField('intro'),
    ]

    subpage_types = ['base.IntranetIndexPage', 'base.IntranetPlainPage', 'staff.StaffPage']

    search_fields = BasePage.search_fields + [
        index.SearchField('intro'),
    ]

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


@register_snippet
class Expertise(models.Model, index.Indexed):
    text = models.CharField(max_length=255, blank=False)
    
    panels = [
        FieldPanel('text'),
    ]
    
    def __str__(self):
        return self.text
    
    search_fields = [
        index.SearchField('text', partial_match=True),
    ]

# Interstitial model for linking the Expertise model to the StaffPage
class StaffPageExpertisePlacement(Orderable, models.Model):
    page = ParentalKey('staff.StaffPage', related_name='expertise_placements')
    expertise = models.ForeignKey('staff.Expertise', related_name='+')

    class Meta:
        verbose_name = "Expertise Placement"
        verbose_name_plural = "Expertise Placements"

    panels = [ 
        SnippetChooserPanel('expertise'),
    ]   

    def __str__(self):
        return self.page.title + " -> " + self.expertise.text

