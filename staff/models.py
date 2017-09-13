from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.db.models.fields import BooleanField, CharField, IntegerField, TextField
from base.models import BasePage, BasePageWithoutStaffPageForeignKeys, DefaultBodyFields
from library_website.settings.base import ORCID_FORMAT, ORCID_ERROR_MSG, PHONE_FORMAT, PHONE_ERROR_MSG
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, ObjectList, PageChooserPanel, StreamFieldPanel, TabbedInterface
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

EMPLOYEE_TYPES = (
    (1, 'Clerical'),
    (2, 'Exempt'),
    (3, 'IT'),
    (4, 'Librarian'),
    (5, 'Non-exempt')
)

POSITION_STATUS = (
    (1, 'Active'),
    (2, 'Vacant'),
    (3, 'Eliminated')
)

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


class StaffPageEmailAddresses(Orderable, models.Model):
    page = ParentalKey('staff.StaffPage', related_name='staff_page_email')
    email = models.EmailField(max_length=254, blank=True)

    panels = [
        FieldPanel('email')
    ]


class StaffPageLibraryUnits(Orderable, models.Model):
    page = ParentalKey('staff.StaffPage', related_name='staff_page_units')
    library_unit = models.ForeignKey(
       'units.UnitPage',
       blank=True,
       null=True,
       on_delete=models.SET_NULL,
       related_name='%(app_label)s_%(class)s_related'
    )

    panels = [
        PageChooserPanel('library_unit')
    ]


class StaffPagePhoneFacultyExchange(Orderable, models.Model):
    phone_regex = RegexValidator(regex=PHONE_FORMAT, message=PHONE_ERROR_MSG)
    page = ParentalKey('staff.StaffPage', related_name='staff_page_phone_faculty_exchange')
    phone_number = models.CharField(validators=[phone_regex], max_length=12, blank=True)
    faculty_exchange = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel('phone_number'),
        FieldPanel('faculty_exchange')
    ]


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

    # editable by HR. 
    cnetid = CharField(
        blank=False,
        help_text='Campus-wide unique identifier which links this record to the campus directory.',
        max_length=255)
    chicago_id = CharField(
        blank=True,
        help_text='Campus-wide unique identifier',
        max_length=9
    )
    display_name = CharField(
        blank=True,
        help_text='Version of this staff person\'s name to display.',
        max_length=255,
        null=True)
    official_name = CharField(
        blank=True,
        help_text='Official version of this staff person\'s name.',
        max_length=255,
        null=True)
    first_name = CharField(
        blank=True,
        help_text='First name, for sorting.',
        max_length=255,
        null=True)
    middle_name = CharField(
        blank=True,
        help_text='Middle name, for sorting.',
        max_length=255,
        null=True)
    last_name = CharField(
        blank=True,
        help_text='Last name, for sorting.',
        max_length=255,
        null=True)
    position_title = CharField(
        blank=True,
        help_text='Position title.',
        max_length=255,
        null=True)
    employee_type = IntegerField(
        choices=EMPLOYEE_TYPES, 
        default=1,
        help_text='Clerical, exempt, IT or Librarian.'
    )
        
    position_status = IntegerField(
        choices=POSITION_STATUS,
        default=1,
        help_text='Help remember and reassign editing responsibilities when staff change positions.'
    )
    supervisor_override = models.ForeignKey(
        'staff.StaffPage',
        blank=True,
        help_text='If supervisor cannot be determined by the staff person\'s unit, specify supervisor here.',
        null=True,
        on_delete=models.SET_NULL,
        related_name='supervisor_override_for'
    )
    supervises_students = BooleanField(default=False)
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
    is_public_persona = BooleanField(
        default=False,
        help_text='(display changes not yet implemented)'
    )
    orcid_regex = RegexValidator(regex=ORCID_FORMAT, message=ORCID_ERROR_MSG)
    orcid = CharField(
        blank=True,
        help_text='See https://orcid.org for more information.',
        max_length=255,
        null=True,
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
        return self.get_subjects() != ''

    @property
    def public_page(self):
        """
        Get a public staff profile page for the
        library expert if one exists.
        """
        from public.models import StaffPublicPage # Should try to do better
        try:
            return StaffPublicPage.objects.get(cnetid=self.cnetid)
        except(IndexError):
            return None

    @property
    def get_supervisors(self):
        if self.supervisor_override:
            return [self.supervisor_override]
        else:
            supervisors = []
            for u in self.staff_page_units.all():
                try:
                    if u.library_unit.department_head.cnetid == self.cnetid:
                        p = u.library_unit.get_parent().specific
                        if p.department_head:
                            supervisors.append(p.department_head)
                    else:
                        supervisors.append(u.library_unit.department_head)
                except AttributeError:
                    continue
            return supervisors 
                    
    def get_subjects(self):
        """
        Get all the subjects for a staff member. 
        Must return a string for elasticsearch.

        Returns:
            String, concatenated list of subjects.
        """
        subject_list = self.staff_subject_placements.values_list('subject', flat=True)
        return '\n'.join(Subject.objects.get(id=subject).name for subject in subject_list)

    def get_subject_objects(self):
        """
        Get all the subject objects for a staff member.

        Returns:
            Set of subjects for a staff member.
        """
        subject_ids = (Subject.objects.get(id=sid) for sid in self.staff_subject_placements.values_list('subject_id', flat=True))
        return set(subject_ids)

    def get_staff(self):
        """
        Get a queryset of the staff members this 
        person supervises.

        TO DO: include a parameter that controls whether this is recursive or not. If it's recursive it should look into the heirarchy of UnitPages to 
        get sub-staff. 

        Returns:
            a queryset of StaffPage objects.
        """

        cnetids = set()
        for s in StaffPage.objects.all():
            if not s == self:
                if s.supervisor_override:
                    cnetids.add(s.cnetid)
                else:
                    for u in s.staff_page_units.filter(library_unit__department_head=self):
                        try:
                            cnetids.add(u.page.cnetid)
                        except:
                            continue

        return StaffPage.objects.filter(cnetid__in=list(cnetids))
         
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

    # for a thread about upcoming support for read-only fields,
    # see: https://github.com/wagtail/wagtail/issues/2893
    human_resources_panels = [
        FieldPanel('cnetid'),
        MultiFieldPanel(
            [
                FieldPanel('display_name'),
                FieldPanel('official_name'),
                FieldPanel('first_name'),
                FieldPanel('middle_name'),
                FieldPanel('last_name'),
                FieldPanel('position_title'),
                InlinePanel('staff_page_email', label='Email Addresses'),
                InlinePanel('staff_page_phone_faculty_exchange', label='Phone Number and Faculty Exchange'),
                InlinePanel('staff_page_units', label='Library Units'),
                FieldPanel('employee_type'),
                FieldPanel('position_status'),
                FieldPanel('supervises_students'),
                PageChooserPanel('supervisor_override'),
            ],
            heading='Human-resources editable fields. These fields will push to the campus directory (where appropriate).'
        ),
        MultiFieldPanel(
            [
                FieldPanel('chicago_id'),
            ],
            heading='Read-only fields. These values are pulled from the campus directory.'
        )
    ]

    search_fields = BasePageWithoutStaffPageForeignKeys.search_fields + [
        index.SearchField('profile_picture'),
        index.SearchField('cv'),
        index.SearchField('libguide_url'),
        index.SearchField('orcid'),
        index.SearchField('get_subjects')
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(Page.promote_panels, heading='Promote'),
        ObjectList(Page.settings_panels, heading='Settings', classname="settings"),
        ObjectList(human_resources_panels, heading='Human Resources Info'),
    ])

    subpage_types = ['base.IntranetIndexPage', 'base.IntranetPlainPage', 'intranetforms.IntranetFormPage', 'intranettocs.TOCPage']

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_context(self, request):
        position_title = self.position_title
        faculty_exchanges = self.staff_page_phone_faculty_exchange.all().values_list('faculty_exchange', flat=True)
        emails = self.staff_page_email.all().values_list('email', flat=True)
        phones = self.staff_page_phone_faculty_exchange.all().values_list('phone_number', flat=True)

        units = set()
        for staff_page_unit in self.staff_page_units.all():
            try:
                unit_title = staff_page_unit.library_unit.get_full_name()
            except:
                unit_title = None
            try:
                unit_url = staff_page_unit.library_unit.intranet_unit_page.first().url
            except:
                unit_url = None
            units.add(json.dumps({
                'title': unit_title,
                'url': unit_url
            }))
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
        context['position_title'] = position_title
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

