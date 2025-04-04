from base.models import BasePage, Email, FaxNumber, LinkedText, PhoneNumber
from django.db import models
from library_website.settings import BUILDINGS
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel, InlinePanel, ObjectList, PageChooserPanel, TabbedInterface
)
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet


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
        index.AutocompleteField('text'),
    ]


class UnitPageRolePlacement(Orderable, models.Model):
    """
    Through table for linking Role snippets to UnitPages.
    """
    page = ParentalKey(
        'units.UnitPage',
        on_delete=models.CASCADE,
        related_name='unit_role_placements'
    )
    role = models.ForeignKey(
        'units.Role', on_delete=models.CASCADE, related_name='+'
    )

    class Meta:
        verbose_name = 'Unit Placement'
        verbose_name_plural = 'Unit Placements'

    panels = [
        FieldPanel('role'),
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
    display_in_library_directory = models.BooleanField(
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
        help_text='The name of this department will hyperlink to this page in \
                   the departmental directory on the library website.',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    location = models.ForeignKey(
        'public.LocationPage',
        blank=True,
        help_text='Controls the address, hours and quick numbers that will \
                   appear on various web pages.',
        null=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_related'
    )
    department_head = models.ForeignKey(
        'staff.StaffPage',
        blank=True,
        help_text='Sorts to the top in staff listings.',
        on_delete=models.SET_NULL,
        null=True,
        related_name='department_head_of'
    )
    department_head_is_interim = models.BooleanField(
        default=False, help_text='For HR reports.'
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
    display_in_campus_directory = models.BooleanField(
        default=True,
        help_text='This unit will appear in reports showing where Wagtail \
                   UnitPages differ from campus directory units.'
    )

    content_panels = Page.content_panels + BasePage.content_panels

    human_resources_panels = [
        PageChooserPanel('department_head'),
        FieldPanel('department_head_is_interim'),
        FieldPanel('display_in_library_directory'),
        FieldPanel('display_in_campus_directory'),
        FieldPanel('display_in_dropdown'),
        FieldPanel('friendly_name'),
        PageChooserPanel('location'),
        FieldPanel('building'),
        PageChooserPanel('public_web_page'),
        FieldPanel('room_number')
    ] + Email.content_panels + [
        InlinePanel('unit_page_phone_number', label='Phone Numbers'),
    ] + FaxNumber.content_panels + LinkedText.content_panels

    subpage_types = ['units.UnitPage']

    search_fields = BasePage.search_fields + [
        index.SearchField('alphabetical_directory_name'),
        index.FilterField('display_in_library_directory')
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading='Content'),
            ObjectList(Page.promote_panels, heading='Promote'),
            ObjectList(
                Page.settings_panels, classname="settings", heading='Settings'
            ),
            ObjectList(human_resources_panels, heading='Human Resources Info'),
        ]
    )

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
        for u in UnitPage.objects.live().filter(
            display_in_library_directory=True
        ):
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

    def get_full_name(self):
        """
        Get a UnitPage's full name according to Wagtail.

        The full name of a UnitPage includes a breadcrumb trail of the titles
        its ancestor UnitPages.

        Example:
        Wagtail contains a UnitPage for "Collections & Access". That Unit Page
        contains "Access Services". The full name for Access Services is
        "Collections & Access - Access Services".

        Compare this method's output with get_campus_directory_full_name().
        """
        return ' - '.join(
            self.get_ancestors(True).type(UnitPage
                                          ).values_list('title', flat=True)
        )

    def get_campus_directory_full_name(self):
        """
        Get a UnitPage's campus directory name.

        The campus directory describes a university department in a three level
        heirarchy: division, department, and sub-department. For library
        departments division is always "Library".

        The library's own view of its org chart has more levels than what we
        can represent in the campus directory, so we skip some levels to make
        room for the departments below it. To skip a level, uncheck the
        display_in_campus_directory boolean on a UnitPage in the Wagtail admin.

        Unchecking that boolean has two effects: first, the
        management command to see if the campus directory and Wagtail are in
        sync will skip this unit. Second, any sub-units will not include
        "Collections & Access" when we retrieve the campus directory's version
        of this unit's full name using this method.

        Example:
        Wagail contains a UnitPage for "Collections & Access - Access
        Services". Access Services has display_in_campus_directory set to
        true, but Collections & Access has that boolean set to false.

        The campus directory full name for Access Services should be "Access
        Services".
        """
        return ' - '.join(
            self.get_ancestors(True).type(UnitPage).filter(
                unitpage__display_in_campus_directory=True
            ).values_list('title', flat=True)
        )

    class Meta:
        ordering = ['title']


class UnitIndexPage(BasePage):
    max_count = 1
    subpage_types = ['units.UnitPage']
    intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ] + BasePage.content_panels

    search_fields = BasePage.search_fields + [
        index.SearchField('intro'),
    ]

    def get_context(self, request):
        context = super(UnitIndexPage, self).get_context(request)

        context['units_hierarchical'] = []
        for u in UnitPage.objects.filter(display_in_library_directory=True):
            if u.contact_point_title:
                unit_page_full_name = ' - '.join(
                    [u.get_full_name(), u.contact_point_title]
                )
            else:
                unit_page_full_name = u.get_full_name()

            context['units_hierarchical'].append(
                {
                    'full_name': unit_page_full_name,
                }
            )

        return context
