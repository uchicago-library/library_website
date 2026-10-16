from django.urls import path, re_path

from . import views

app_name = "design_system"

urlpatterns = [
    path("llms.txt", views.llms_txt, name="llms"),
    path("tokens.json", views.tokens_json, name="tokens_json"),
    # The HTML pages. A folder in content/ with the same name would be hidden.
    path("tokens/", views.tokens, name="tokens"),
    path("demos/", views.demos, name="demos"),
    path("demos/<slug:slug>/", views.demo, name="demo"),
    # A page's Markdown source: /design/<page>.md, or /design/index.md for home.
    re_path(
        r"^(?P<slug>[\w-]+(?:/[\w-]+)*)\.md$",
        views.markdown_source,
        name="markdown",
    ),
    re_path(r"^(?:(?P<slug>[\w-]+(?:/[\w-]+)*)/)?$", views.page, name="page"),
    # Anything else under /design/ gets the design system's 404, not the site's.
    re_path(r"", views.not_found),
]
