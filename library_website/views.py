from django.http import Http404
from django.shortcuts import render
from wagtail.images.models import Image
from wagtail.models import Site


def library_404_view(request, exception=Http404):

    site_name = Site.find_for_request(request).site_name

    class Link:

        def __init__(self, text, url):
            self.text = text
            self.url = url

    def context_404(site_name):
        if site_name == "Public":
            return {
                "extention":
                "base/public_base.html",
                "links": [
                    Link(
                        "Ask a Librarian",
                        "https://www.lib.uchicago.edu/research/help/ask-librarian/"
                    ),
                    Link(
                        "Library Digital Collections",
                        "https://www.lib.uchicago.edu/collex/"
                    ),
                    Link("Library Homepage", "https://www.lib.uchicago.edu/")
                ],
                "helptext1":
                "Let us know that we have a missing page.",
                "helptext2":
                " We will do our best to rectify the issue."
            }
        else:
            return {
                "extention":
                "intranethome/intranet_home_page.html",
                "koala":
                Image.objects.get(title="Adventure Koala"),
                "links": [
                    Link(
                        "Return to Loop Homepage",
                        "https://loop.lib.uchicago.edu/"
                    )
                ],
                "helptext1":
                "Let us know that we have a missing page. Contact ",
                "helptext_email":
                "intranet@lib.uchicago.edu",
                "helptext2":
                " and we will do our best to rectify the issue.",
                "tabs":
                True
            }

    context = context_404(site_name)

    return render(request, '404.html', context)
