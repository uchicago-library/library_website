from django.shortcuts import render

def collections(request):
    view = request.GET.get('view', 'collections')
    return render(request, 'lib_collections/collections_index_page.html', {
        'view': view
    })
