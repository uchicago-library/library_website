from django.http import Http404
from django.shortcuts import render
from wagtail.models import Site


def library_404_view(request, exception=Http404):
    site_name = Site.find_for_request(request).site_name
    if site_name == "Public":
        return render(request, '404_lib.html')
    else:
        return render(request, '404_loop.html')
