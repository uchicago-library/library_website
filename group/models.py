from django.db import models
from django.db.models.fields import CharField, TextField
from staff.models import StaffPage
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.models import Page

class GroupMember(models.Model):
	group = models.ForeignKey('GroupPage')
	role = CharField(
		blank=True,
		max_length=255)
	staff = models.ForeignKey('staff.StaffPage')

class GroupPage(Page):
	name = TextField(
		blank=True)
	email = CharField(
		blank=True,
		max_length=255)
	intro = TextField(
		blank=True)
	meeting_location = CharField(
		blank=True,
		max_length=255)
	meeting_time = CharField(
		blank=True,
		max_length=255)

GroupPage.content_panels = Page.content_panels + [
	FieldPanel('name'),
	FieldPanel('email'),
	FieldPanel('intro'),
	FieldPanel('meeting_location'),
	FieldPanel('meeting_time')
]

class GroupIndexPage(Page):
	intro = TextField()

	content_panels = Page.content_panels + [
		FieldPanel('intro')
	]

	subpage_types = ['group.GroupPage']
