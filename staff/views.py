from directory_unit.models import DirectoryUnit
from django.db.models import Q
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from intranetunits.models import IntranetUnitsIndexPage, IntranetUnitsPage
from subjects.models import Subject
from staff.models import StaffPage, StaffPagePageVCards, StaffPageSubjectPlacement

from wagtail.wagtailcore.models import Page
from wagtail.wagtailsearch.models import Query
from wagtail.contrib.wagtailsearchpromotions.models import SearchPromotion

def staff(request):
    library = request.GET.get('library', None)
    page = request.GET.get('page', 1)
    query = request.GET.get('query', None)
    subject = request.GET.get('subject', None)
    view = request.GET.get('view', 'staff')

    staff_pages_all = None

    if library:
        # get a queryset of units from each library building, then get a list of distinct StaffPage pks for each queryset. 
        if library == 'Eckhart Library':
            eckhart_units = DirectoryUnit.objects.get(name='Eckhart Library').get_descendants(True)
            staff_pks = StaffPagePageVCards.objects.filter(unit__in=eckhart_units).values_list('page', flat=True).distinct()
        elif library == 'Crerar Library':
            crerar_units = DirectoryUnit.objects.get(name='Science Libraries').get_descendants(True)
            eckhart_units = DirectoryUnit.objects.get(name='Eckhart Library').get_descendants(True)
            staff_pks = StaffPagePageVCards.objects.filter(unit__in=crerar_units).exclude(unit__in=eckhart_units).values_list('page', flat=True).distinct()
        elif library == 'D\'Angelo Law Library':
            dangelo_units = DirectoryUnit.objects.get(name='D\'Angelo Law Library').get_descendants(True)
            staff_pks = StaffPagePageVCards.objects.filter(unit__in=dangelo_units).values_list('page', flat=True).distinct()
        elif library == 'SSA Library':
            ssa = DirectoryUnit.objects.get(name='Social Service Administration Library (SSA)').get_descendants(True)
            staff_pks = StaffPagePageVCards.objects.filter(unit__in=ssa).values_list('page', flat=True).distinct()
        elif library == 'Regenstein Library':
            crerar = DirectoryUnit.objects.get(name='Science Libraries').get_descendants(True)
            dangelo = DirectoryUnit.objects.get(name='D\'Angelo Law Library').get_descendants(True)
            ssa = DirectoryUnit.objects.get(name='Social Service Administration Library (SSA)').get_descendants(True)
            staff_pks = StaffPagePageVCards.objects.all().exclude(unit__in=crerar).exclude(unit__in=dangelo).exclude(unit__in=ssa).values_list('page', flat=True).distinct()
        elif library == 'Special Collections Research Center':
            scrc = DirectoryUnit.objects.get(name='Special Collections Research Center').get_descendants(True)
            staff_pks = StaffPagePageVCards.objects.all().filter(unit__in=scrc).values_list('page', flat=True).distinct()
        elif library == 'Mansueto':
            mansueto = DirectoryUnit.objects.filter(Q(name='Mansueto') | Q(name='Mansueto Library'))
            staff_pks = StaffPagePageVCards.objects.all().filter(unit__in=mansueto).values_list('page', flat=True).distinct()
            
        # get StaffPages themselves from the pk list. 
        staff_pages_all = StaffPage.objects.filter(pk__in=staff_pks).order_by('last_name', 'first_name')

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

    # Set up paging. 
    paginator = Paginator(staff_pages_all, 50)
    try:
        staff_pages = paginator.page(page)
    except PageNotAnInteger:
        staff_pages = paginator.page(1)
    except EmptyPage:
        staff_pages = paginator.page(paginator.num_pages)

    units = [{
        'title': IntranetUnitsIndexPage.objects.first().title,
        'url': IntranetUnitsIndexPage.objects.first().url,
        'children': [],
    }]

    # for each unit page get a list of the page's "intranet units page" or
    # "intranet units index page" ancestors. Check to see if this
    # particular ancestor already exists in the units tree. If it doesn't
    # exist, create it. Then continue on, one descendant at a time, either
    # adding new levels or using the existing ones if they're already there
    # from previous unit pages. 
    for intranetunitspage in IntranetUnitsPage.objects.live():
        ancestors = [IntranetUnitsIndexPage.objects.first()] + list(IntranetUnitsPage.objects.ancestor_of(intranetunitspage)) + [intranetunitspage]
        currentlevel = units
        while ancestors:
            ancestor = ancestors.pop(0)
            if str(ancestor.content_type) in ['intranet units page', 'intranet units index page']:
                nextlevels = list(filter(lambda g: g['url'] == ancestor.url, currentlevel))
                if nextlevels:
                    currentlevel = nextlevels[0]['children']
                else:
                    newnode = {
                        'title': ancestor.title,
                        'url': ancestor.url,
                        'internal_location': ancestor.internal_location,
                        'internal_phone_number': ancestor.internal_phone_number,
                        'children': [],
                    }
                    currentlevel.append(newnode)
                    currentlevel = newnode['children']

    def alphabetize_units(currentlevel):
        for node in currentlevel:
            node['children'] = alphabetize_units(node['children'])
        return sorted(currentlevel, key=lambda c: c['title'])
    units = alphabetize_units(units)

    def get_html(currentlevel):
        if not currentlevel:
            return ''
        else:
            return "<ul>" + "".join(list(map(lambda n: "<li><a href='" + n['url'] + "'>" + n['title'] + "</a>" + ("<br/>" + n['internal_phone_number'] if n['internal_phone_number'] else "") + ("<br/>" + n['internal_location'] if n['internal_location'] else "") + get_html(n['children']) + "</li>", currentlevel))) + "</ul>"
    intranetunits_html = get_html(units[0]['children'])

    # JEJ
    # annotate IntranetUnitsPage objects with unit.fullName
    '''
    for i in IntranetUnitsPage.objects.live().order_by
    '''

    

    # Pagination
    '''
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)
    '''
    
    # Subjects
    subject_pks = StaffPageSubjectPlacement.objects.all().values_list('subject', flat=True).distinct()
    subjects = Subject.objects.filter(pk__in=subject_pks).values_list('name', flat=True)

    return render(request, 'staff/staff_index_page.html', {
        'intranetunits_html': intranetunits_html,
        'libraries': ["Regenstein Library", "Crerar Library", "D'Angelo Library", "Eckhart Library", "Mansueto", "Special Collections Research Center", "SSA Library"],
        'library': library,
        'query': query,
        'subject': subject,
        'subjects': subjects,
        'subjects': subjects,
        'staff_pages': staff_pages,
        'view': view
    })
