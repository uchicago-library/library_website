from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.core.fields import RichTextField
from wagtail.search import index
from wagtail.snippets.models import register_snippet


@register_snippet
class ReusableContent(models.Model, index.Indexed):
    STYLE_TYPE_CHOICES = (
        ('general-box', 'General'),
        ('info-box', 'Informative'),
        ('alert-box', 'Alert'),
    )

    title = models.CharField(
        max_length=155,
        blank=False,
        help_text='A friendly name only used in the Wagtail admin'
    )
    sidebar_heading = models.CharField(
        max_length=100,
        blank=True,
        help_text='An optional header that will display above your \
        content as an <h3> in the right sidebar. Ignored in page bodies'
    )
    content = RichTextField(
        blank=False,
        help_text='Reusable content that can be displayed in the right \
        sidebar or a page body'
    )
    style_type = models.CharField(
        max_length=12,
        choices=STYLE_TYPE_CHOICES,
        default='general-box',
        verbose_name='Styling',
        help_text=
        '"Informative" is a light blue background and "Alert" is a light red background',
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('title'),
                FieldPanel('sidebar_heading'),
                FieldPanel('content'),
                FieldPanel('style_type'),
            ],
            heading='Reusable Content'
        )
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Reusable Content'
        verbose_name_plural = 'Reusable Content'

    search_fields = [
        index.SearchField('content'),
    ]
