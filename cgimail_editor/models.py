from django.core.exceptions import ValidationError
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page

from base.models import BasePage


class DocumentationSource(Orderable, models.Model):
    """
    Documentation sources for AI context.
    Allows either URL or internal page selection.
    """

    page = ParentalKey(
        "cgimail_editor.CGIMailFormEditorPage",
        related_name="documentation_sources",
        on_delete=models.CASCADE,
    )

    url = models.URLField(
        blank=True,
        help_text="External documentation URL (can be any website)",
    )

    internal_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Internal Wagtail page",
    )

    description = models.CharField(
        max_length=255,
        help_text="Context for AI (e.g., 'Developer documentation', 'CGIMail reference')",
    )

    panels = [
        FieldPanel("url"),
        FieldPanel("internal_page"),
        FieldPanel("description"),
    ]

    class Meta:
        verbose_name = "Documentation Source"
        verbose_name_plural = "Documentation Sources for AI context"

    def clean(self):
        super().clean()
        if not self.url and not self.internal_page:
            raise ValidationError("Either URL or Internal Page must be provided")
        if self.url and self.internal_page:
            raise ValidationError("Provide either URL or Internal Page, not both")

    def __str__(self):
        return self.description or self.url or str(self.internal_page)


class CGIMailFormEditorPage(BasePage):
    """
    AI-powered CGIMail form generator tool.
    Accessible only on Loop (intranet).
    Named "Rebecca" after the librarian who inspired the project.
    """

    max_count = 1

    # Introduction text
    intro = RichTextField(
        blank=True,
        help_text="Introductory text displayed at the top of the tool",
    )

    # AI Configuration
    system_prompt = models.TextField(
        default="""You are an expert at generating CGIMail form JSON configurations for the University of Chicago Library website.

Your task is to generate valid JSON that follows the CGIMailFormSchema exactly. Output ONLY valid JSON with no explanations or markdown.

Key requirements:
1. The first section must always be hidden with a 'rcpt' field containing the recipient surrogate.
   These should never be email addresses. Surrogates are just text. Do not convert them into email
   addresses.
2. Use appropriate field types: text, email, textarea, select, checkbox, radio, hidden.
3. Group related fields using fieldset (with legend) or group (side-by-side).
4. Add helpful placeholder text and help text where appropriate.
5. Mark required fields with required: true.
6. Select boxes: Options for these are not lists of strings. They are lists of objects that have
   value and text attributes. Always give these a default "unselected" state.
7. Conditional fields: Use enabledWhen to show a field only when another field has a specific value.
   - enabledWhen.field must match the controlling field's name attribute (not id)
   - enabledWhen.value must exactly match one of the controlling field's option values
   Example: To show "Select your year" only for undergraduates:
   First field:  {"name": "UChicago_Affiliation", "options": [{"value": "", "text": "-- Select --", "disabled": true, "selected": true}, {"value": "Undergraduate student", ...}]}
   Second field: {"name": "Year", "enabledWhen": {"field": "UChicago_Affiliation", "value": "Undergraduate student"}}""",
        help_text="System prompt sent to the AI model",
    )

    ai_model = models.CharField(
        max_length=50,
        default="chatgpt-4o-latest",
        choices=[
            ("gpt-3.5-turbo", "GPT-3.5 Turbo"),
            ("gpt-4o", "GPT-4o"),
            ("gpt-4-turbo", "GPT-4 Turbo"),
            ("gpt-5.1", "GPT-5.1"),
            ("o3", "o3"),
            ("chatgpt-4o-latest", "ChatGPT-4o Latest"),
        ],
        help_text="OpenAI model to use for generation",
    )

    # Template for quick start
    template_description = models.TextField(
        blank=True,
        default="""Create an appointment request form with:
- Name (required)
- Email address (required)
- UChicago affiliation dropdown (Undergraduate student, Graduate student, Faculty or instructor, Staff, Alumni, Visitor / Not UChicago)
- If undergraduate, year dropdown (1st Year, 2nd Year, 3rd Year, Senior)
- Major, department, or program text field
- Research question summary (required, large text area)
- Is this for a UChicago course? dropdown (Yes, No)
- If yes, course name and number text field
- Research done so far (large text area)
- Accommodation notes (large text area)""",
        help_text="Pre-populated template description (click 'Load Example' to use)",
    )

    # Page configuration
    subpage_types = []
    parent_page_types = [
        "intranethome.IntranetHomePage",
        "base.IntranetPlainPage",
        "base.IntranetIndexPage",
    ]

    content_panels = (
        Page.content_panels
        + [
            FieldPanel("intro"),
        ]
        + BasePage.content_panels
    )

    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            [
                FieldPanel("system_prompt"),
                FieldPanel("ai_model"),
            ],
            heading="AI Configuration",
        ),
        InlinePanel("documentation_sources"),
        MultiFieldPanel(
            [
                FieldPanel("template_description"),
            ],
            heading="Template",
        ),
    ]

    class Meta:
        verbose_name = "CGIMail Form Editor Page"

    def get_context(self, request):
        context = super().get_context(request)

        # API endpoints for React component
        context["surrogate_api_url"] = "/cgimail-editor/api/surrogates/"
        context["generate_api_url"] = "/cgimail-editor/api/generate/"
        context["fetch_docs_api_url"] = "/cgimail-editor/api/fetch-docs/"

        # Pass configuration to React
        context["ai_model"] = self.ai_model
        context["template_description"] = self.template_description
        context["system_prompt"] = self.system_prompt

        return context
