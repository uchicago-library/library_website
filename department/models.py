from django.db import models
from django.db.models.fields import CharField, TextField
from staff.models import StaffPage
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.models import Page

class DepartmentPage(Page):
	name = TextField(
		blank=True)
	email = CharField(
		blank=True,
		max_length=255)
	intro = TextField(
		blank=True)

	subpage_types = ['department.DepartmentPage']

DepartmentPage.content_panels = Page.content_panels + [
	FieldPanel('name'),
	FieldPanel('email'),
	FieldPanel('intro')
]

class DepartmentIndexPage(Page):
	intro = TextField()

	content_panels = Page.content_panels + [
		FieldPanel('intro')
	]

	subpage_types = ['department.DepartmentPage']
