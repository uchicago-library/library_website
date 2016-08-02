from django.db import models
from wagtail.wagtailcore.models import Page, Site
from base.models import PublicBasePage, DefaultBodyFields, ContactFields
from wagtail.wagtailsearch import index
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel, StreamFieldPanel
from .utils import get_chat_status, get_chat_status_css
from library_website.settings import PHONE_FORMAT, PHONE_ERROR_MSG
from django.core.validators import RegexValidator

class AskPage(PublicBasePage, ContactFields):
    """
    Page type for Ask A Librarian pages.
    """

    ask_widget_name = models.CharField(max_length=100, blank=True)
    reference_resources = RichTextField(blank=True)
    body = StreamField(DefaultBodyFields())
    phone_regex = RegexValidator(regex=PHONE_FORMAT, message=PHONE_ERROR_MSG)
    secondary_phone_number = models.CharField(validators=[phone_regex], max_length=12, blank=True)
    schedule_appointment_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
        help_text='Link to a contact form'
    )
    visit_page = models.ForeignKey(
            'wagtailcore.Page',
            null=True,
            blank=True,
            related_name='+',
            on_delete=models.SET_NULL,
            help_text='Link to a location or hours page'
        )


    subpage_types = ['public.StandardPage', 'public.PublicRawHTMLPage']

    content_panels = Page.content_panels + [
        FieldPanel('ask_widget_name'),
        FieldPanel('reference_resources'),
        MultiFieldPanel(
            [
                PageChooserPanel('link_page'),
                FieldPanel('link_external'),
            ],
            heading='Contact Form'
        ),
        MultiFieldPanel(
            [
                FieldPanel('email'),
                FieldPanel('phone_number'),
                FieldPanel('secondary_phone_number'),
                PageChooserPanel('visit_page'),
                PageChooserPanel('schedule_appointment_page'), 
            ],
            heading='General Contact'
        ),
        StreamFieldPanel('body'),
    ] + PublicBasePage.content_panels

    search_fields = PublicBasePage.search_fields + [
        index.SearchField('ask_widget_name'),
        index.SearchField('reference_resources'),
        index.SearchField('body'),
        index.SearchField('email'),
        index.SearchField('email_label'),
        index.SearchField('phone_number'),
        index.SearchField('body'),
    ]

    @property 
    def ask_form_name(self):
        """
        Get the name of the chat widget.

        Returns:
            String, name of the ask widget.
        """
        return self.ask_widget_name

    @property
    def contact_link(self):
        """
        Return an html link for contacting 
        a librarian by email.
        """
        text = '<i class="fa fa-envelope-o fa-2x"></i> Email' 
        if self.link_page:
            return '<a href="%s">%s</a>' % (self.link_page.url, text)
        elif self.email:
            return '<a href="mailto:%s">%s</a>' % (self.email, text)
        else:
            return False

    @property
    def has_right_sidebar(self):
        """
        Determine if a right sidebar should
        be displayed on AskPages.

        Returns:
            boolean
        """
        fields = [self.contact_link, self.phone_number, self.secondary_phone_number, self.schedule_appointment_page, self.visit_page]
        if self.base_has_right_sidebar():
            return True
        else:
            for field in fields:
                if field:
                    return True
        return False

    def get_context(self, request):
        context = super(AskPage, self).get_context(request)
        context['ask_pages'] = AskPage.objects.live()
 
        return context
