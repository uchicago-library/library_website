from django.shortcuts import render
from lib_collections.models import CollectionPage, CollectionPageFormatPlacement, CollectionPageSubjectPlacement, ExhibitPage, ExhibitPageSubjectPlacement, Format
from public.models import LocationPage
from staff.models import StaffPage
from subjects.models import Subject, SubjectParentRelations
from wagtail.wagtailsearch.backends import get_search_backend

import datetime

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
        collections = CollectionPage.objects.all()
	
        if digital:
            #collections = collections.filter(collection_placements__format__text='Digital')
            collections = collections.filter(title="A Century of Progress International Exposition Publications")


        if format:
            collections = collections.filter(collection_placements__format__text=format)

        if search:
            collections = collections.search(search)

        if subject:
            subject_ids = Subject.objects.get(name=subject).get_descendants()
            collections = collections.filter(collection_subject_placements__subject__in=subject_ids)

    # fiter exhibits.
    exhibits = []
    exhibits_current = []
    if view == 'exhibits':
        exhibits = ExhibitPage.objects.live().order_by('title')

        if digital:
            exhibits = exhibits.exclude(web_exhibit_url = '')

        if location:
            exhibits = exhibits.filter(exhibit_location__title=location)

        if subject:
            subject_ids = Subject.objects.get(name=subject).get_descendants()
            exhibits = exhibits.filter(exhibit_subject_placements__subject__in=subject_ids)

        exhibits_current = exhibits.filter(exhibit_open_date__lt = datetime.datetime.now().date()).filter(exhibit_close_date__gt = datetime.datetime.now().date())

        if search:
            exhibits = exhibits.search(search).results()
            exhibits_current = exhibits_current.search(search).results()

    # FORMATS AND SUBJECTS THAT MAKE SENSE FOR THE QUERIES THAT HAVE HAPPENED SO FAR.

    # we'll need some kind of way to only get formats and subjects for things where it's possible here.  
    # sorted(CollectionPageFormatPlacement.objects.all().values_list('format__text', flat=True).distinct())
    formats = Format.objects.all().values_list('text', flat=True)

    # the formats pulldown should skip 'Digital'. That shows up as a checkbox. 
    formats_pulldown = ['Archives & Manuscripts', 'Audio', 'Books & Journals', \
'Images', 'Maps', 'Microform', 'Music Scores', 'Photographs', 'Reference Works', \
'Statistics & Datasets', 'Video']

    # locations
    locations = sorted(LocationPage.objects.live().values_list('title', flat=True))

    subjects = []
    # this needs to fold the see alsos in. 

    # JEJ TODO:
    # make a new subjects list to populate the subject pulldown.
    # list subjects whose parent has no parent, plus law. So grandchild subjects online.

    # for the code below, list all subjects that are children of the subjects in the list
    # above, plus anything with a libguide id. right now that is equal to
    # business, medicine and law. See DB's "collections subjects" lucid chart for more 
    # info. 

    subjects_queryset = Subject.objects.all()

    if search:
        s = get_search_backend()
        subjects_queryset = s.search(search, Subject)

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

    subjects_pulldown = ['Area & Cultural Studies', 'Arts', 'Business', \
'Humanities', 'Law', 'Literature', 'Medicine', 'Sciences, Biological', \
'Sciences, Physical', 'Social Sciences', 'Social Services', 'Special Collections']

    return render(request, 'lib_collections/collections_index_page.html', {
        'collections': collections,
        'digital': digital,
        'exhibits': exhibits,
        'exhibits_current': exhibits_current,
        'format': format,
        'formats': formats,
        'formats_pulldown': formats_pulldown,
        'location': location,
        'locations': locations,
        'search': search,
        'subject': subject,
        'subjects': subjects,
        'subjects_pulldown': subjects_pulldown,
        'view': view
    })
