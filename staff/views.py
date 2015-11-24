from django.shortcuts import render

from staff.models import StaffIndexPage

def index(request):
    staff_index_page = StaffIndexPage.objects.all()[0]

    staff_pages = []
    for child in staff_index_page.get_descendants():
        try:
            date = child.first_published_at.strftime('%B %d').replace(' 0', ' ')
        except:
            date = ''
        
        
        staff_pages.append({
            'date':  date,
            'title': child.title,
            'url':   child.url
        })

    return render(request, 'staff/staff_index_page.html', {
        'staff_pages': staff_pages,
        'self': {
            'intro': staff_index_page.intro,
            'title': staff_index_page.title
        }
    })
