from django.shortcuts import render
from lib_collections.models import CollectionPage, CollectionPageFormatPlacement, Format
from subjects.models import Subject

def collections(request):
    # formats
    collection_placement_ids = CollectionPage.objects.all().values_list('collection_placements', flat=True)
    collection_page_format_placement_ids = CollectionPageFormatPlacement.objects.filter(id__in=collection_placement_ids)
    format_ids = CollectionPageFormatPlacement.objects.filter(id__in=collection_page_format_placement_ids).values_list('format', flat=True).distinct()
    formats = Format.objects.filter(id__in=format_ids).values_list('text', flat=True)
    formats = sorted(formats)

    subjects = []
    # this needs to fold the see alsos in. 
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

    # PARAMETERS
    format = request.GET.get('format', None)
    if not format in formats:
        format = None
    view = request.GET.get('view', 'collections')

    return render(request, 'lib_collections/collections_index_page.html', {
        'collections': CollectionPage.objects.all(),
        'format': format,
        'formats': formats,
        'subjects': subjects,
        'view': view
    })
