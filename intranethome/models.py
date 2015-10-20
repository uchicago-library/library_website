from __future__ import unicode_literals

from django.core.validators import EmailValidator, RegexValidator
from django.db import models

from django.db.models.fields import CharField, TextField, IntegerField
from django.utils.translation import ugettext_lazy

from wagtail.wagtailadmin.edit_handlers import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

class IntranetHomePage(Page):
	body = RichTextField()

	content_panels = Page.content_panels + [
		FieldPanel('body')
	]

	subpage_types = ['group.GroupIndexPage', 'news.NewsIndexPage', 'staff.StaffIndexPage']
