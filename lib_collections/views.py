from django.shortcuts import render
from lib_collections.models import CollectionPage, CollectionPageFormatPlacement, ExhibitPage, Format
from public.models import LocationPage
from subjects.models import Subject

def collections(request):
    # PARAMETERS
    digital = request.GET.get('digital', None)
    format = request.GET.get('format', None)
    if not format in Format.objects.all().values_list('text', flat=True):
        format = None
    location = request.GET.get('location', None)
    if not location in LocationPage.objects.live().values_list('title', flat=True):
        location = None
    subject = request.GET.get('subject', None)
    if not subject in Subject.objects.all().values_list('name', flat=True):
        subject = None
    view = request.GET.get('view', 'collections')
    if not view in ['collections', 'exhibits', 'subjects']:
        view = 'collections'

    # filter collections.
    collections = CollectionPage.objects.all()

    if digital:
        collections = collections.filter(collection_placements__format__text='Digital')

    if format:
        collections = collections.filter(collection_placements__format__text=format)

    if subject:
        collections = collections.filter(collection_subject_placements__subject__name=subject)

    # fiter exhibits.
    exhibits = ExhibitPage.objects.live()
    if location:
        exhibits = exhibits.filter(exhibit_location__title=location)
    if subject:
        exhibits = exhibits.filter(exhibit_subject_placements__subject__name=subject)

    # FORMATS AND SUBJECTS THAT MAKE SENSE FOR THE QUERIES THAT HAVE HAPPENED SO FAR.

    # we'll need some kind of way to only get formats and subjects for things where it's possible here.  
    # sorted(CollectionPageFormatPlacement.objects.all().values_list('format__text', flat=True).distinct())
    formats = Format.objects.all().values_list('text', flat=True)

    # the formats pulldown should skip 'Digital'. That shows up as a checkbox. 
    tmp = sorted(list(set(CollectionPage.objects.all().values_list('collection_placements__format__text', flat=True))))
    formats_pulldown = [f for f in tmp if f not in ['Digital']]

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
    for s in Subject.objects.all():
        subjects.append({
            'see_also': None,
            'name': s.name
        })
        for see_also in s.see_also.all():
            subjects.append({
                'name': see_also.alias,
                'see_also': see_also.snippet.name
            })
    subjects = sorted(subjects, key=lambda s: s['name'])

    # for the subject pulldown, find subjects that are first generation children- their parents should have no parent. 
    # still need these:
    # Area and Cultural Studies
    # Social Sciences
    # Biological Sciences
    # Physical Sciences
    subjects_pulldown = ['Art, Architecture and Photography', 'Business', 'Humanities and Social Science', 'Law', 'Medicine']

    return render(request, 'lib_collections/collections_index_page.html', {
        'collections': collections,
        'digital': digital,
        'exhibits': exhibits,
        'format': format,
        'formats': formats,
        'formats_pulldown': formats_pulldown,
        'locations': locations,
        'subject': subject,
        'subjects': subjects,
        'subjects_pulldown': subjects_pulldown,
        'view': view
    })
