from django.urls import path

from . import views

urlpatterns = [
    path("", views.ags_upload_page, name="ags_upload_page"),
    path("js/", views.display_js, name="display_js"),
]
