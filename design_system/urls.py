from django.urls import path, re_path

from . import views

app_name = "design_system"

urlpatterns = [
    path("llms.txt", views.llms_txt, name="llms"),
    path("tokens.json", views.tokens_json, name="tokens"),
    re_path(r"^(?:(?P<slug>[\w-]+(?:/[\w-]+)*)/)?$", views.page, name="page"),
]
