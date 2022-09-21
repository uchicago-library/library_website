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
  # search result snippet title. 
  title = models.CharField(
    verbose_name="title",
    max_length=255,
    help_text="The page title as you'd like it to be seen by the public"
  )
  # the date this record was created or last updated. 
  datestamp = models.DateTimeField(
    verbose_name="datestamp"
  )
  # search result snippet link. 
  url = models.URLField(
    max_length=300,
    verbose_name="url"
  )
  # search result snippet description.
  description = models.TextField(
    verbose_name="description"
  )
  # the "content" to be indexed. 
  content = models.TextField(
    verbose_name="content"
  )

  search_fields = [
    index.SearchField('title', boost=4, partial_match=True),
    index.SearchField('description', partial_match=True),
    index.SearchField('content', partial_match=True)
  ]

 
class LibGuidesSearchableContent(SearchableContent):
  tags = models.TextField( 
    verbose_name="tags"
  )
  subjects = models.TextField(
    verbose_name="subjects"
  )

  search_fields = [
    index.SearchField('content', boost=0.5, partial_match=True),
    index.SearchField('description', partial_match=True),
    index.SearchField('subjects'),
    index.SearchField('tags'),
    index.SearchField('title', boost=4, partial_match=True),
  ]


class LibGuidesAssetsSearchableContent(SearchableContent):
  pass
