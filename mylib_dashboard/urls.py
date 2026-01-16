"""
URL configuration for MyLib Dashboard API endpoints.
"""

from django.urls import path

from . import views

app_name = "mylib_dashboard"

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("loans/", views.loans, name="loans"),
    path("holds/", views.holds, name="holds"),
    path("fines/", views.fines, name="fines"),
    path("account-blocks/", views.account_blocks, name="account_blocks"),
]
