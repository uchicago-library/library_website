from django.db.models import Q
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from intranetunits.models import IntranetUnitsIndexPage, IntranetUnitsPage
from subjects.models import Subject
from staff.models import StaffPage, StaffPageSubjectPlacement
from units.views import get_staff_pages_for_library

from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.models import Image
from wagtail.wagtailsearch.models import Query
from wagtail.contrib.wagtailsearchpromotions.models import SearchPromotion

def staff(request):
    library = request.GET.get('library', None)
    page = request.GET.get('page', 1)
    query = request.GET.get('query', None)
    subject = request.GET.get('subject', None)
    view = request.GET.get('view', 'staff')

    staff_pages = []
    staff_pages_all = []
    flat_units = []

    if view == 'staff':
        if library:
            staff_pages_all = get_staff_pages_for_library(library)
        else:
            staff_pages_all = StaffPage.objects.live().order_by('last_name', 'first_name')
    
        if subject:
            subject_pk = Subject.objects.get(name=subject).pk
            staff_pks = StaffPageSubjectPlacement.objects.filter(subject=subject_pk).values_list('page', flat=True).distinct()
    
            if staff_pages_all:
                staff_pages_all = staff_pages_all.filter(pk__in=staff_pks).order_by('last_name', 'first_name')
            else:
                staff_pages_all = StaffPage.objects.filter(pk__in=staff_pks).order_by('last_name', 'first_name')
    
        if query:
            if staff_pages_all:
                staff_pages_all = staff_pages_all.search(query)
            else:
                staff_pages_all = StaffPage.objects.live().search(query)
    
        if not library and not subject and not query:
            staff_pages_all = StaffPage.objects.live().order_by('title').order_by('last_name', 'first_name')
    elif view == 'department':
        if query:
            for i in IntranetUnitsPage.objects.live().search(query):
                if hasattr(i.unit, 'fullName'):
                    flat_units.append({
                        'internal_location': i.internal_location,
                        'internal_phone_number': i.internal_phone_number,
                        'library': i.unit.get_parent_library_name(),
                        'title': i.unit.fullName,
                        'url': i.url,
                    })
        else:
            for i in IntranetUnitsPage.objects.live().order_by('unit__fullName'):
                if hasattr(i.unit, 'fullName'):
                    flat_units.append({
                        'internal_location': i.internal_location,
                        'internal_phone_number': i.internal_phone_number,
                        'library': i.unit.get_parent_library_name(),
                        'title': i.unit.fullName,
                        'url': i.url,
                    })

    # Set up paging. 
    paginator = Paginator(staff_pages_all, 50)
    try:
        staff_pages = paginator.page(page)
    except PageNotAnInteger:
        staff_pages = paginator.page(1)
    except EmptyPage:
        staff_pages = paginator.page(paginator.num_pages)

    # Subjects
    subject_pks = StaffPageSubjectPlacement.objects.all().values_list('subject', flat=True).distinct()
    subjects = Subject.objects.filter(pk__in=subject_pks).values_list('name', flat=True)

    default_image = Image.objects.get(title="Default Placeholder Photo")

    return render(request, 'staff/staff_index_page.html', {
        'default_image': default_image,
        'flat_intranet_units': flat_units,
        'libraries': ["Regenstein Library", "Crerar Library", "D'Angelo Law Library", "Eckhart Library", "Mansueto", "Special Collections Research Center", "SSA Library"],
        'library': library,
        'query': query,
        'subject': subject,
        'subjects': subjects,
        'subjects': subjects,
        'staff_pages': staff_pages,
        'view': view
    })
