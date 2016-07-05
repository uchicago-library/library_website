from django.shortcuts import render
from lib_collections.models import CollectionPage, CollectionPageFormatPlacement, CollectionPageSubjectPlacement, ExhibitPage, ExhibitPageSubjectPlacement, Format
from public.models import LocationPage
from staff.models import StaffPage
from subjects.models import Subject, SubjectParentRelations
from wagtail.wagtailimages.models import Image
from wagtail.wagtailsearch.backends import get_search_backend

import datetime
import re

def collections(request):
    # PARAMETERS
    digital = request.GET.get('digital', None)
    if not digital == 'on':
        digital = None
    format = request.GET.get('format', None)
    if not format in Format.objects.all().values_list('text', flat=True):
        format = None
    location = request.GET.get('location', None)
    if not location in LocationPage.objects.live().values_list('title', flat=True):
        location = None
    search = request.GET.get('search', None)
    subject = request.GET.get('subject', None)
    if not subject in Subject.objects.all().values_list('name', flat=True):
        subject = None
    view = request.GET.get('view', 'collections')
    if not view in ['collections', 'exhibits', 'subjects']:
        view = 'collections'

    # filter collections.
    collections = []
    if view == 'collections':
        filter_arguments = {}

        # format
        if digital or format:
            filter_arguments['collection_placements__format__text__in'] = []
        if digital:
            filter_arguments['collection_placements__format__text__in'].append('Digital')
        if format:
            filter_arguments['collection_placements__format__text__in'].append(format)

        # subject 
        if subject:
            filter_arguments['collection_subject_placements__subject__in'] = Subject.objects.get(name=subject).get_descendants()

        # search
        if search:
            filter_arguments['id__in'] = list(map(lambda s: s.id, CollectionPage.objects.live().search(search)))

        collections = CollectionPage.objects.live().filter(**filter_arguments).distinct()

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

        exhibits = ExhibitPage.objects.live().filter(**filter_arguments).distinct()
        exhibits_current = exhibits.filter(exhibit_open_date__lt=datetime.datetime.now().date(), exhibit_close_date__gt=datetime.datetime.now().date()).distinct()

        if digital:
            exhibits = exhibits.exclude(web_exhibit_url = '')
            exhibits_current = exhibits_current.exclude(web_exhibit_url = '')

        if search:
            exhibits = exhibits.search(search).results()
            exhibits_current = exhibits_current.search(search).results()

        if not search:
            exhibits = sorted(exhibits, key=lambda e: re.sub(r'^(A|An|The) ', '', e.title))
            exhibits_current = sorted(exhibits_current, key=lambda e: re.sub('r^(A|An|The) ', '', e.title))

    # formats.
    formats = Format.objects.all().values_list('text', flat=True)

    # the formats pulldown should skip 'Digital'. That shows up as a checkbox. 
    formats_pulldown = ['Archives & Manuscripts', 'Audio', 'Books & Journals', \
'Images', 'Maps', 'Microform', 'Music Scores', 'Photographs', 'Reference Works', \
'Statistics & Datasets', 'Video']

    # locations
    locations = sorted(list(set(ExhibitPage.objects.exclude(exhibit_location=None).values_list('exhibit_location__title', flat=True))))

    subjects = []
    # for the code below, list all subjects that are children of the subjects in the list
    # above, plus anything with a libguide id. right now that is equal to
    # business, medicine and law. See DB's "collections subjects" lucid chart for more 
    # info. 

    subjects_queryset = Subject.objects.all()

    if search:
        s = get_search_backend()
        subjects_queryset = s.search(search, Subject)

    if subject:
        subject_ids = Subject.objects.get(name=subject).get_descendants()
        subjects_queryset = subjects_queryset.filter(id__in=subject_ids)

    for s in subjects_queryset:
        parents = sorted(SubjectParentRelations.objects.filter(child=s).values_list('parent__name', flat=True))
        subjects.append({
            'has_collections': CollectionPageSubjectPlacement.objects.filter(subject__in = s.get_descendants()).exists(),
            'has_exhibits': ExhibitPageSubjectPlacement.objects.filter(subject__in = s.get_descendants()).exists(),
            'has_subject_specialists': StaffPage.objects.filter(staff_subject_placements__subject = s).exists(),
            'libguide_url': s.libguide_url,
            'name': s.name,
            'parents': parents,
            'see_also': None
        })
        for see_also in s.see_also.all():
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
        'view': view
    })
