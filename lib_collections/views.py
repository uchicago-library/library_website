from django.shortcuts import render
from lib_collections.models import CollectionPage, CollectionPageFormatPlacement, CollectionPageSubjectPlacement, ExhibitPage, ExhibitPageSubjectPlacement, Format
from public.models import LocationPage
from staff.models import StaffPage, StaffPageSubjectPlacement
from subjects.models import Subject, SubjectParentRelations
from wagtail.wagtailimages.models import Image
from wagtail.wagtailsearch.backends import get_search_backend
from ask_a_librarian.utils import get_chat_status, get_chat_status_css, get_unit_chat_link
from public.models import StandardPage
from library_website.settings import PUBLIC_HOMEPAGE
from base.utils import get_hours_and_location
from units.models import UnitPage

import datetime
import re
import pickle

from django.core.cache import caches, cache
from django.views.decorators.cache import cache_page
from django.db import connection
from django.conf import settings

def do_line_profiler(view=None, extra_view=None):
    import line_profiler

    def wrapper(view):
        def wrapped(*args, **kwargs):
            prof = line_profiler.LineProfiler()
            prof.add_function(view)
            if extra_view:
                [prof.add_function(v) for v in extra_view]
            with prof:
                resp = view(*args, **kwargs)
            prof.print_stats()
            return resp

        return wrapped

    if view:
        return wrapper(view)

    return wrapper

# Python Line Profiler, use when debugging
#@do_line_profiler
def collections(request):
    # PARAMETERS
    default_cache = caches['default']

    digital = request.GET.get('digital', None)
    if not digital == 'on':
        digital = None
    format = request.GET.get('format', None)
    if not Format.objects.filter(text=format).exists():
        format = None
    location = request.GET.get('location', None)
    if not LocationPage.objects.live().filter(title=location).exists():
        location = None
    search = request.GET.get('search', None)
    subject = request.GET.get('subject', None)
    if not Subject.objects.all().filter(name=subject).exists():
        subject = None

    # broken... what does this even do???
    unit = request.GET.get('unit', None)

    view = request.GET.get('view', 'collections')
    if not view in ['collections', 'exhibits', 'subjects']:
        view = 'collections'

    # filter collections.
    collections = []
    if view == 'collections':
        filter_arguments = {}

        # format
        if format:
            filter_arguments['collection_placements__format__text'] = format

        # digital
        if digital:
            filter_arguments['collection_placements__format__text'] = 'Digital'

        # subject 
        if subject:
            filter_arguments['collection_subject_placements__subject__in'] = Subject.objects.get(name=subject).get_descendants()

        # search
        if search:
            filter_arguments['id__in'] = list(map(lambda s: s.id, CollectionPage.objects.live().search(search)))

        # unit
        if unit:
            filter_arguments['unit'] = UnitPage.objects.get(title=unit)

        collections = CollectionPage.objects.live().filter(**filter_arguments).distinct().select_related('thumbnail').prefetch_related('collection_subject_placements')

        # sort browses by title, omitting leading articles. 
        if not search:
            collections = sorted(collections, key=lambda c: re.sub(r'^(A|An|The) ', '', c.title))

    # fiter exhibits.
    exhibits = []
    exhibits_current = []
    if view == 'exhibits':
        filter_arguments = {}

        if location:
            filter_arguments['exhibit_location__title'] = location

        if subject:
            filter_arguments['exhibit_subject_placements__subject__in'] = Subject.objects.get(name=subject).get_descendants()

        if unit:
            filter_arguments['unit'] = UnitPage.objects.get(title=unit)

        if digital:
            filter_arguments['web_exhibit'] = True

        exhibits = ExhibitPage.objects.live().filter(**filter_arguments).distinct().select_related('thumbnail', 'exhibit_location').prefetch_related('exhibit_subject_placements')
        exhibits_current = exhibits.filter(exhibit_open_date__lt=datetime.datetime.now().date(), exhibit_close_date__gt=datetime.datetime.now().date()).distinct()

        if search:
            exhibits = exhibits.search(search).results()
            exhibits_current = exhibits_current.search(search).results()

        if not search:
            exhibits = sorted(exhibits, key=lambda e: re.sub(r'^(A|An|The) ', '', e.title))
            exhibits_current = sorted(exhibits_current, key=lambda e: re.sub('r^(A|An|The) ', '', e.title))

    # locations
    locations = sorted(list(set(ExhibitPage.objects.exclude(exhibit_location=None).values_list('exhibit_location__title', flat=True))))

    # formats.
    formats = Format.objects.all().values_list('text', flat=True)

    # the formats pulldown should skip 'Digital'. That shows up as a checkbox. 
    formats_pulldown = ['Archives & Manuscripts', 'Audio', 'Books & Journals', \
'Images', 'Maps', 'Microform', 'Music Scores', 'Photographs', 'Reference Works', \
'Statistics & Datasets', 'Video']

    subjects = []
    if view == 'subjects':
        # for the code below, list all subjects that are children of the subjects in the list
        # above, plus anything with a libguide id. right now that is equal to
        # business, medicine and law. See DB's "collections subjects" lucid chart for more 
        # info. 
        subjects_queryset = Subject.objects.all().prefetch_related('see_also')

        if search:
            s = get_search_backend()
            subjects_queryset = s.search(search, Subject)

        if subject:
            subject_ids = Subject.objects.get(name=subject).get_descendants()
            subjects_queryset = subjects_queryset.filter(id__in=subject_ids)

        subjects_with_collections = set(CollectionPageSubjectPlacement.objects.values_list('subject', flat=True))
        subjects_with_exhibits = set(ExhibitPageSubjectPlacement.objects.all().values_list('subject', flat=True))
        subjects_with_specialists = set(StaffPageSubjectPlacement.objects.values_list('subject', flat=True))

        qs = SubjectParentRelations.objects.all().prefetch_related('panels')

        for s in subjects_queryset:
            if default_cache.has_key('subject_id_%s' % s.id):
                subjects_list_entry = default_cache.get('subject_id_%s' % s.id)
            else:
                subject_descendants = default_cache.get('descendants_%s' % s.id)

                if not subject_descendants:
                    subject_descendants = set(s.get_descendants().values_list('id', flat=True))
                    default_cache.set('descendants_%s' % s.id, subject_descendants, 60*5)

                parents = qs.filter(child=s).order_by('parent__name').values_list('parent__name', flat=True).prefetch_related('subject')
                has_collections = bool(subjects_with_collections.intersection(subject_descendants))
                has_exhibits = bool(subjects_with_exhibits.intersection(subject_descendants))
                has_subject_specialists = s.id in subjects_with_specialists

                subjects_list_entry = {
                    'has_collections': has_collections,
                    'has_exhibits': has_exhibits,
                    'has_subject_specialists': has_subject_specialists,
                    'libguide_url': s.libguide_url,
                    'name': s.name,
                    'parents': parents,
                    'see_also': None
                }
                default_cache.set('subject_id_%s' % s.id, subjects_list_entry)

            subjects.append(subjects_list_entry)

            see_also_qs = s.see_also.all()
            if see_also_qs:
                for see_also in see_also_qs:
                    subjects.append({
                        'has_collections': False,
                        'has_exhibits': False,
                        'has_subject_specialists': False,
                        'libguide_url': None,
                        'name': see_also.alias,
                        'parents': [],
                        'see_also': see_also.snippet.name
                    })
        subjects = sorted(subjects, key=lambda s: s['name'])

    # for the subject pulldown, find subjects that are first generation children- their parents should have no parent. 
    # still need these:
    # Area and Cultural Studies
    # Social Sciences
    # Biological Sciences
    # Physical Sciences

    subjects_pulldown = ['Area & Cultural Studies', 'Arts', \
'Biological Sciences', 'Business', 'Humanities', 'Law', 'Literature', \
'Medicine', 'Physical Sciences', 'Social Sciences', 'Social Services', \
'Special Collections']

    default_image = None
    try:
        default_image = Image.objects.get(title="Default Placeholder Photo")
    except:
        pass

    # Set context variables for templates
    home_page = StandardPage.objects.live().get(id=PUBLIC_HOMEPAGE)
    location_and_hours = get_hours_and_location(home_page)
    page_location = str(location_and_hours['page_location'])
    page_unit = location_and_hours['page_unit']

#    if not default_cache.has_key('exhibits_current_list'):
#        exhibits_current_list = set(exhibits)
#        default_cache.set('exhibits_current_list', exhibits_current_list)

    return render(request, 'lib_collections/collections_index_page.html', {
        'collections': collections,
        'breadcrumb_div_css': 'col-md-12 breadcrumbs hidden-xs hidden-sm',
        'content_div_css': 'container body-container col-xs-12 col-lg-11 col-lg-offset-1',
        'default_image': default_image,
        'digital': digital,
        'exhibits': exhibits,
        'exhibits_current': exhibits_current,
        'format': format,
        'formats': formats,
        'formats_pulldown': formats_pulldown,
        'location': location,
        'locations': locations,
        'search': search,
        'self': {
            'title': 'Collections & Exhibits'
        },
        'subject': subject,
        'subjects': subjects,
        'subjects_pulldown': subjects_pulldown,
        'view': view,
        'page_unit': str(page_unit),
        'page_location': page_location,
        'address': location_and_hours['address'],
        'chat_url': get_unit_chat_link(page_unit, request),
        'chat_status': get_chat_status('uofc-ask'),
        'chat_status_css': get_chat_status_css('uofc-ask'),
        'hours_page_url': home_page.get_hours_page(request),
    })
