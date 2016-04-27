from django.shortcuts import render
from subjects.models import Subject

def collections(request):
    view = request.GET.get('view', 'collections')

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

    return render(request, 'lib_collections/collections_index_page.html', {
        'subjects': subjects,
        'view': view
    })
