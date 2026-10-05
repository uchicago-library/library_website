from django.urls import path

from . import views

app_name = "cgimail_editor"

urlpatterns = [
    path("api/surrogates/", views.fetch_surrogates, name="fetch_surrogates"),
    path("api/fetch-docs/", views.fetch_documentation, name="fetch_documentation"),
    path("api/generate/", views.generate_form_json, name="generate_form_json"),
]
