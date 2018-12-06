from django.db import models
from wagtail.search import index

class SearchableContent(index.Indexed, models.Model):
  identifier = models.CharField(
    verbose_name="identifier",
    max_length=255,
    help_text="A unique identifier, like a primary key or URL, from the \
      producer of this data. This identifier should be unique to that \
      producer, but it does not necessarily have to be unique across this \
      entire database table."
  )
  title = models.CharField(
    verbose_name="title",
    max_length=255,
    help_text="The page title as you'd like it to be seen by the public"
  )
  datestamp = models.DateTimeField(
    verbose_name="datestamp"
  )
  url = models.URLField(
    verbose_name="url"
  )
  description = models.TextField(
    verbose_name="description"
  )
  content = models.TextField(
    verbose_name="subject"
  )
  tag = models.CharField(
    verbose_name="tag",
    max_length=255
  )

  search_fields = [
    index.SearchField('title', boost=4, partial_match=True),
    index.SearchField('description', partial_match=True),
    index.SearchField('content', partial_match=True)
  ]
