from django.db import models
from django.db.models.fields import CharField, TextField
from intranetbase.models import IntranetBasePage
from staff.models import StaffPage
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page

class DepartmentPage(IntranetBasePage):
    intro = TextField(
        blank=True)
    location = CharField(
        blank=True,
        max_length=255)
    telephone = CharField(
        blank=True,
        max_length=255)
    email = CharField(
        blank=True,
        max_length=255)
    body = RichTextField()

    subpage_types = ['department.DepartmentPage', 'intranetbase.PlainPage', 'intranetbase.SidebarPage']

DepartmentPage.content_panels = Page.content_panels + [
    FieldPanel('intro'),
    FieldPanel('location'),
    FieldPanel('telephone'),
    FieldPanel('email'),
    FieldPanel('body')
] + IntranetBasePage.content_panels

class DepartmentIndexPage(Page):
    intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    subpage_types = ['department.DepartmentPage']
