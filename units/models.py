from django.db import models
from library_website.settings import PHONE_FORMAT, PHONE_ERROR_MSG
from wagtail.wagtailcore.models import Orderable, Page
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, FieldRowPanel, \
    InlinePanel, MultiFieldPanel, ObjectList, PageChooserPanel, \
    StreamFieldPanel, TabbedInterface
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from modelcluster.fields import ParentalKey
from django.core.validators import RegexValidator
from base.models import BasePage, DefaultBodyFields, Email, FaxNumber, \
    LinkedText, PhoneNumber

BUILDINGS = (
    (1, 'Crerar Library'),
    (2, 'D\'Angelo Law Library'),
    (3, 'Eckhart Library'),
    (4, 'Mansueto Library'),
    (5, 'Regenstein Library'),
    (6, 'Special Collections Research Center'),
    (7, 'SSA Library')
)


class Tree(object):
    def __init__(self, name='root', unit_page=None, children=None):
        self.name = name
        self.unit_page = unit_page
        self.children = []
        if children is not None:
            for child in children:
                self.add_child(child)

    def __repr__(self):
        return self.name

    def add_child(self, node):
        assert isinstance(node, Tree)
        if self.get_child(node.name) is None:
            self.children.append(node)
            self.children.sort(key=lambda t: t.name)

    def get_child(self, name):
        c = 0
        while c < len(self.children):
            if self.children[c].name == name:
                return self.children[c]
            c = c + 1
        return None


@register_snippet
class Role(models.Model, index.Indexed):
    """
    Snippet for roles.
    """
    text = models.CharField(max_length=255, blank=False)

    panels = [
        FieldPanel('text'),
    ]

    class Meta:
        verbose_name = 'Unit Role'
        verbose_name_plural = 'Unit Roles'

    def __str__(self):
        return self.text

    search_fields = [
        index.SearchField('text', partial_match=True),
    ]


class UnitPageRolePlacement(Orderable, models.Model):
    """
    Through table for linking Role snippets to UnitPages.
    """
    page = ParentalKey('units.UnitPage', related_name='unit_role_placements')
    role = models.ForeignKey('units.Role', related_name='+')

    class Meta:
        verbose_name = 'Unit Placement'
        verbose_name_plural = 'Unit Placements'

    panels = [
        SnippetChooserPanel('role'),
    ]

    def __str__(self):
        return self.page.title + ' -> ' + self.role.text


class UnitPagePhoneNumbers(Orderable, PhoneNumber):
    page = ParentalKey('units.UnitPage', related_name='unit_page_phone_number')
    panels = PhoneNumber.content_panels


class UnitPage(BasePage, Email, FaxNumber, LinkedText):
    """
    Basic structure for units and departments.
    """
    contact_point_title = models.CharField(max_length=255, blank=True)
    alphabetical_directory_name = models.CharField(max_length=255, blank=True)
    friendly_name = models.CharField(
        blank=True,
        help_text='e.g.: "Ask a (friendly_name) librarian", or "view all \
                   (friendly_name) study spaces."',
        max_length=255,
    )
    display_in_directory = models.BooleanField(
        default=True,
        help_text='Display this unit in the library\'s departmental \
                   directory.'
    )
    display_in_dropdown = models.BooleanField(
        default=False,
        help_text='Display this unit in the Wagtail admin when a UnitPage \
                   is selectable in a dropdown menu.'
    )
    room_number = models.CharField(
        blank=True,
        help_text='This will appear in the departmental directory on the \
                   library website.',
        max_length=32
    )
    public_web_page = models.ForeignKey(
        'wagtailcore.Page',
        blank=True,
        help_text='A link to this page will appear in the departmental \
                   directory on the library website.',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    location = models.ForeignKey(
        'public.LocationPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_related'
    )
    department_head = models.ForeignKey(
        'staff.StaffPage',
        blank=True,
        on_delete=models.SET_NULL,
        null=True,
        related_name='department_head_of'
    )
    department_head_is_interim = models.BooleanField(
        default=False
    )
    building = models.IntegerField(
        choices=BUILDINGS,
        default=5,
        help_text='The physical building where this unit is located.'
    )
    street_address = models.CharField(max_length=255, blank=True)
    internal_email = models.EmailField(max_length=255, blank=True)
    faculty_exchange = models.CharField(max_length=32, blank=True)
    public_url = models.CharField(max_length=255, blank=True)
    public_url_label = models.CharField(max_length=255, blank=True)
    is_a_division = models.BooleanField(default=False)
    display_in_campus_directory = models.BooleanField(default=True)

    content_panels = Page.content_panels + [
        FieldPanel('friendly_name'),
        FieldPanel('display_in_directory'),
        FieldPanel('display_in_dropdown'),
        FieldPanel('room_number'),
        PageChooserPanel('public_web_page'),
        FieldPanel('location'),
    ] + BasePage.content_panels

    human_resources_panels = [
        PageChooserPanel('department_head'),
        FieldPanel('department_head_is_interim'),
        FieldPanel('building'),
        FieldPanel('street_address'),
        FieldPanel('faculty_exchange'),
        FieldPanel('public_url'),
        FieldPanel('public_url_label'),
        FieldPanel('is_a_division'),
        FieldPanel('display_in_campus_directory'),
        FieldPanel('internal_email'),
    ] + Email.content_panels + [
        InlinePanel('unit_page_phone_number', label='Phone Numbers'),
    ] + FaxNumber.content_panels + LinkedText.content_panels

    subpage_types = ['units.UnitPage']

    search_fields = BasePage.search_fields + [
        index.SearchField('alphabetical_directory_name'),
        index.FilterField('display_in_directory')
    ]

    edit_handler = TabbedInterface([
        ObjectList(
            content_panels,
            heading='Content'
        ),
        ObjectList(
            Page.promote_panels,
            heading='Promote'
        ),
        ObjectList(
            Page.settings_panels,
            classname="settings",
            heading='Settings'
        ),
        ObjectList(
            human_resources_panels,
            heading='Human Resources Info'
        ),
    ])

    def __str__(self):
        return self.get_full_name()

    def get_building(self):
        if self.building is not None:
            for b in BUILDINGS:
                if self.building == b[0]:
                    return b[1]
        return ''

    @staticmethod
    def hierarchical_units():
        records = []
        for u in UnitPage.objects.live().filter(display_in_directory=True):
            records.append([u.get_full_name().split(' - '), u])

        # sort records by full name.
        records = sorted(records, key=lambda r: r[1].get_full_name())

        hierarchical_units = Tree()
        for record, unit_page in records:
            t = hierarchical_units
            f = 0
            while f < len(record):
                next_child = t.get_child(record[f])
                if next_child is None:
                    next_child = Tree(record[f], unit_page)
                    t.add_child(next_child)
                t = next_child
                f = f + 1

        return hierarchical_units

    def get_full_name(self, library_directory=True):
        return ' - '.join(self.get_ancestors(True).type(UnitPage).values_list(
            'title',
            flat=True
        ))

    def get_campus_directory_full_name(self):
        return ' - '.join(self.get_ancestors(True).type(UnitPage).filter(
            unitpage__display_in_campus_directory=True
        ).values_list('title', flat=True))

    class Meta:
        ordering = ['title']


class UnitIndexPage(BasePage):
    intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ] + BasePage.content_panels

    search_fields = BasePage.search_fields + [
        index.SearchField('intro'),
    ]

    subpage_types = ['units.UnitPage']

    def get_context(self, request):
        context = super(UnitIndexPage, self).get_context(request)

        context['units_hierarchical'] = []
        for u in UnitPage.objects.filter(display_in_directory=True):
            if u.contact_point_title:
                unit_page_full_name = ' - '.join(
                    [u.get_full_name(), u.contact_point_title]
                )
            else:
                unit_page_full_name = u.get_full_name()

            context['units_hierarchical'].append({
                'full_name': unit_page_full_name,
            })

        return context
