"""
URL configuration for MyLib Dashboard API endpoints.
"""

from django.urls import path

from . import views

app_name = "mylib_dashboard"

urlpatterns = [
    # FOLIO endpoints
    path("profile/", views.profile, name="profile"),
    path("loans/", views.loans, name="loans"),
    path("holds/", views.holds, name="holds"),
    path("fines/", views.fines, name="fines"),
    path("account-blocks/", views.account_blocks, name="account_blocks"),
    # ILLiad endpoints
    path("downloads/", views.downloads, name="downloads"),
    path("ill-in-process/", views.ill_in_process, name="ill_in_process"),
    path(
        "scan-deliver-in-process/",
        views.scan_deliver_in_process,
        name="scan_deliver_in_process",
    ),
    # LibCal endpoints
    path("reservations/", views.reservations, name="reservations"),
    path("special-collections/seats/", views.sc_seats, name="sc_seats"),
    # Paging requests (items being retrieved from stacks/storage)
    path("paging-requests/", views.paging_requests, name="paging_requests"),
    # Aeon endpoints
    path("special-collections/materials/", views.sc_materials, name="sc_materials"),
]
