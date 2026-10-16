from django.urls import path, re_path

from . import views

app_name = "design_system"

urlpatterns = [
    path("llms.txt", views.llms_txt, name="llms"),
    path("tokens.json", views.tokens_json, name="tokens"),
    # A page's Markdown source; a folder's is <folder>/index.md.
    re_path(
        r"^(?P<slug>[\w-]+(?:/[\w-]+)*)\.md$",
        views.markdown_source,
        name="markdown",
    ),
    re_path(r"^(?:(?P<slug>[\w-]+(?:/[\w-]+)*)/)?$", views.page, name="page"),
    # Anything else under /design/ gets the design system's 404, not the site's.
    re_path(r"", views.not_found),
]
