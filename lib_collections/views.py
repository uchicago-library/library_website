from django.shortcuts import render

def collections(request):
    return render(request, 'lib_collections/collections_index_page.html', {})
