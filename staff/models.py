from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.db.models.fields import BooleanField, CharField, TextField

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.models import Page
from wagtail.wagtaildocs.models import Document
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index

class StaffTitle(models.Model):
	staff = models.ForeignKey('staff.StaffPage')
	title = CharField(
		max_length=255)
	department = CharField(
		max_length=255)
	sub_department = CharField(
		max_length=255)
	phone = CharField(
		max_length=255)
	faculty_exchange = CharField(
		max_length=255)

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
	email = CharField(
		max_length=255,
		validators=[EmailValidator()],
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

	content_panels = Page.content_panels + [
                ImageChooserPanel('profile_picture'),
		FieldPanel('alphabetize_name_as'),
		FieldPanel('bio'),
		DocumentChooserPanel('cv'),
		FieldPanel('is_public_persona')]

class StaffIndexPage(Page):
	intro = TextField()
	content_panels = Page.content_panels + [
		FieldPanel('intro')
	]

	search_fields = Page.search_fields + ( # Inherit search_fields from Page
		index.SearchField('intro'),
	)

	subpage_types = ['staff.StaffPage']
