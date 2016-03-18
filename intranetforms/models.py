from django.db import models

from base.models import get_breadcrumbs, AbstractBase
from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import (FieldPanel, InlinePanel,
    MultiFieldPanel)
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailforms.models import AbstractEmailForm, AbstractFormField

class IntranetFormField(AbstractFormField):
    page = ParentalKey('IntranetFormPage', related_name='form_fields')

class IntranetFormPage(AbstractEmailForm, AbstractBase):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro', classname="full"),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
        MultiFieldPanel([
            FieldPanel('to_address', classname="full"),
            FieldPanel('from_address', classname="full"),
            FieldPanel('subject', classname="full"),
        ], "Email")
    ] + AbstractBase.content_panels

    promote_panels = AbstractEmailForm.promote_panels + AbstractBase.left_sidebar_panels

    def get_context(self, request):
        context = super(IntranetFormPage, self).get_context(request)
        context['breadcrumbs'] = get_breadcrumbs(self)
        return context

