from django.db import models
from django.db.models.fields import TextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

class NewsPage(Page):
        feature_image = models.ForeignKey(
                'wagtailimages.Image',
                null=True,
                blank=True,
                on_delete=models.SET_NULL,
                related_name='+')
        body = RichTextField();
        excerpt = models.TextField(blank=True)
        thumbnail_image = models.ForeignKey(
                'wagtailimages.Image',
                null=True,
                blank=True,
                on_delete=models.SET_NULL,
                related_name='+')

        content_panels = [ 
                FieldPanel('title'),
                FieldPanel('body', classname="full"),
                FieldPanel('excerpt'),
                ImageChooserPanel('feature_image'),
                ImageChooserPanel('thumbnail_image'),
        ] 

class NewsIndexPage(Page):
	intro = TextField()

	content_panels = Page.content_panels + [
		FieldPanel('intro')
	]

	subpage_types = ['home.NewsPage']
