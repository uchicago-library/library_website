import sys
from django.core.management.base import BaseCommand, CommandError
from wagtail.core.models import Page
import django.apps

def get_all_page_models():
    """
    Get a listing of all page models in the site.
    TODO: refactor into own command.

    Returns:
        Set
    """
    page_types = set([])
    for model in django.apps.apps.get_models():
        if issubclass(model, Page):
            page_types.add((model.__module__, model.__name__))
    return page_types

PAGE_TYPES = get_all_page_models()

# Import all page types
for pt in PAGE_TYPES:
    code = 'from ' + pt[0] + ' import ' + pt[1]
    exec(code)

class Command(BaseCommand):
    """
    Get the optimal subset of pages for a test database.
    The real test database will be larger than this since
    pages in this subset will have dependencies that we will
    get with another script.
    """

    def add_arguments(self, parser):
        """
        Add required positional options and optional
        named arguments.
        """
        # Required positional options
        #parser.add_argument('test', nargs='+', type=str)

    def handle(self, *args, **options):
        """
        Main command.
        """
        self.stdout.write('Getting pages...' )

        home_page = set([3378])
        kiosk_pages = set([1752, 1754, 1755, 1753, 1797, 1756, 1758])
        hours_page = set([4084])
        ask_pages = set([p.id for p in set(AskPage.objects.live())])
        location_pages = set([p.id for p in LocationPage.objects.live()])
        collection_pages = set([p.id for p in CollectionPage.objects.live()])
        exhibit_pages = set([p.id for p in ExhibitPage.objects.live()])
        news_pages = set([591, 592, 593, 594, 595, 596, 598, 601, 611, 663, 665, 743, 898, 902])
        public_raw_html_pages = set([4084, 4127, 4568])
        redirect_pages = set([4717, 6474])
        toc_pages = set([407, 418, 419])
        standard_pages = set([1633, 1634, 1636, 1638, 1648, 1656, 1664, 1672,
        1673, 1752, 1753, 1754, 1755, 1756, 1758, 1833, 1837, 1843, 1844, 3269,
        3275, 3284, 3285, 3289, 3314, 3369, 3896, 3942, 4145, 4234, 4510, 4534,
        4643, 4715, 4841, 5911, 5961, 5962, 5967, 7071, 7072])
        one_of_each = self._get_one_of_each(PAGE_TYPES) # First of every page type

        all_pages = home_page | kiosk_pages | hours_page | ask_pages | location_pages | news_pages | public_raw_html_pages | redirect_pages | standard_pages | toc_pages | collection_pages | exhibit_pages | one_of_each

        formatted_pages = ''.join(self._format_pages(all_pages))

        return '[' + formatted_pages + ']'


    def _get_classanme_and_id(self, p):
        """
        Get the full classname of a page object.

        Args:
            p: page object

        Returns:
            String representing a tuple where the first item
            would be a classname and the second item would be
            an integer if it were real. 
        """
        spc = p.specific.__class__
        pc = spc.__module__ + '.' + spc.__name__
        pid = p.id
        return '(' + '\'' + str(pc) + '\'' + ', ' + str(pid) + '), '


    def _format_pages(self, pages):
        """
        Get pages and format them as a list of tuples
        where the first item in each tuple is a classname
        and the second item is a page id.

        Args:
            pages: set of integers (page IDs).
        """
        for page in pages:
            yield self._get_classanme_and_id(Page.objects.get(id=page))

    def _get_one_of_each(self, page_types):
        """
        Get one of every page type. Will only get the
        first instance of every page type. 

        Args:
            page_types: set of tuples where the first
            item in the tuple is the module string and
            the second item is the classname string.
        """
        retval = set([])
        for p in page_types:
            code = p[1] + '.objects.live().first()'
            first_page = eval(code)
            if first_page:
                retval.add(first_page.id)
        return retval


