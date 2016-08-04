from django.shortcuts import render
from django.http import JsonResponse
import json
import urllib
from wagtail.wagtailcore.models import Page, Site

def page_url(request):
    """
    Restful api for getting the url for 
    a wagtail page. 
    """
    if request.method == 'GET':
        pid = int(request.GET['id'])
        try:
            page = Page.objects.live().get(id=pid) 
            current_site = Site.find_for_request(request)
            return JsonResponse(
                {
                    'relative': page.relative_url(current_site),
                    'absolute': page.url,
                }
            )
        except(Page.DoesNotExist):
            return JsonResponse(
                {
                    'relative': None,
                    'absolute': None,
                }
            )
