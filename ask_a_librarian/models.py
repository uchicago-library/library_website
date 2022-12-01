from wagtail.blocks import RichTextBlock
from django.core.validators import RegexValidator
from django.db import models
from wagtail.admin.panels import (
    FieldPanel, MultiFieldPanel, PageChooserPanel
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index

from base.models import ContactFields, DefaultBodyFields, PublicBasePage, RawHTMLBlock, ReusableContentBlock
from library_website.settings import LIBCHAT_WIDGET_URL, PHONE_ERROR_MSG, PHONE_FORMAT


class AskPage(PublicBasePage, ContactFields):
    """
    Page type for Ask A Librarian pages.
    """

    intro = StreamField(
        [
            ('paragraph', RichTextBlock()),
            ('reusable_content_block', ReusableContentBlock()),
            ('html', RawHTMLBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )
    ask_widget_name = models.CharField(max_length=100, blank=True)
    body = StreamField(
        DefaultBodyFields(
            null=True,
            blank=True,
        ),
        use_json_field=True,
    )
    reference_resources = RichTextField(
        blank=True,
        help_text='Links to guide links and other \
        Ask pages. Make new sections with Header 3'
    )
    phone_regex = RegexValidator(regex=PHONE_FORMAT, message=PHONE_ERROR_MSG)
    secondary_phone_number = models.CharField(
        validators=[phone_regex],
        max_length=12,
        blank=True,
        verbose_name="SMS Number"
    )
    schedule_appointment_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
        help_text='Shows up as Schedule icon link. Link to a contact form'
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
        FieldPanel('intro'),
        FieldPanel('ask_widget_name'),
        FieldPanel('body'),
        MultiFieldPanel(
            [
                FieldPanel('phone_number'),
                FieldPanel('secondary_phone_number'),
                PageChooserPanel('visit_page'),
                PageChooserPanel('schedule_appointment_page'),
            ],
            heading='Other Ways to Ask: General Contact'
        ),
        MultiFieldPanel(
            [
                PageChooserPanel('link_page'),
                FieldPanel('link_external'),
                FieldPanel('email'),
            ],
            heading='Other Ways to Ask: Email Icon Link',
            help_text='Shows up as Email icon link. Can only have one.'
        ),
        FieldPanel('reference_resources'),
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
        text = '<span class="material-icons ask-icons" aria-hidden="true">mail_outline</span> Email'
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
        fields = [
            self.contact_link, self.phone_number, self.secondary_phone_number,
            self.schedule_appointment_page, self.visit_page
        ]
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
        context['libchat_widget_url'] = LIBCHAT_WIDGET_URL

        return context
