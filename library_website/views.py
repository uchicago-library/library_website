from django.http import Http404
from django.shortcuts import render
from wagtail.images.models import Image
from wagtail.models import Site


def library_404_view(request, exception=Http404):

    is_default = Site.find_for_request(request).is_default_site

    class Link:

        def __init__(self, text, url):
            self.text = text
            self.url = url

    def context_404(is_default):

        if is_default:
            return {
                "404_page_template_switcher":"base/public_base.html",
                "links": [
                    Link("Ask a Librarian", "/research/help/ask-librarian/"),
                    Link("Library Digital Collections", "/collex/"),
                    Link("Library Homepage", "/")
                ],
                "helptext1":
                "Let us know that we have a missing page.",
                "helptext2":
                " We will do our best to rectify the issue."
            }
        else:
            return {
                "404_page_template_switcher":"intranethome/intranet_home_page.html",
                "koala": Image.objects.get(title="Adventure Koala"),
                "links": [Link("Return to Loop Homepage", "/")],
                "helptext1":
                "Let us know that we have a missing page. Contact ",
                "helptext_email": "intranet@lib.uchicago.edu",
                "helptext2": " and we will do our best to rectify the issue.",
                "tabs": True
            }

    context = context_404(is_default)

    return render(request, '404.html', context, status=404)
