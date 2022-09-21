from base.models import AbstractBase, get_breadcrumbs
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel, InlinePanel, MultiFieldPanel
)
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.fields import RichTextField


class IntranetFormField(AbstractFormField):
    page = ParentalKey('IntranetFormPage', related_name='form_fields')


class IntranetFormPage(AbstractEmailForm, AbstractBase):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro', classname="full"),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
        MultiFieldPanel(
            [
                FieldPanel('to_address', classname="full"),
                FieldPanel('from_address', classname="full"),
                FieldPanel('subject', classname="full"),
            ], "Email"
        )
    ] + AbstractBase.content_panels

    promote_panels = AbstractEmailForm.promote_panels + \
        AbstractBase.left_sidebar_panels

    search_fields = []

    subpage_types = []

    def get_context(self, request):
        context = super(IntranetFormPage, self).get_context(request)
        context['breadcrumbs'] = get_breadcrumbs(self)
        return context
