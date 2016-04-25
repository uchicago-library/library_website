from directory_unit.models import DirectoryUnit
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render
from django.utils.html import escape
from staff.models import StaffPage, StaffPagePageVCards, StaffPageSubjectPlacement, VCard
from subjects.models import Subject
from units.models import UnitPage

def get_subjects():
    subject_pks = StaffPageSubjectPlacement.objects.all().values_list('subject', flat=True).distinct()
    subjects = Subject.objects.filter(pk__in=subject_pks).values_list('name', flat=True)
    return subjects

def get_departments(library = None):
    if library == 'Crerar Library':
        departments = [
            'Science Libraries - Administration',
            'Science Libraries - Astronomy and Astrophysics',
            'Science Libraries - Biochemistry and Molecular Biology',
            'Science Libraries - Chemistry',
            'Science Libraries - Computer Science',
            'Science Libraries - Crerar Library Access Services',
            'Science Libraries - Ecology and Evolution',
            'Science Libraries - Geophysical Sciences',
            'Science Libraries - Human Genetics',
            'Science Libraries - Mathematics',
            'Science Libraries - Medicine',
            'Science Libraries - Microbiology',
            'Science Libraries - Molecular Genetics and Cell Biology',
            'Science Libraries - Neurobiology',
            'Science Libraries - Nursing',
            'Science Libraries - Organismal Biology and Anatomy',
            'Science Libraries - Pharmacological and Physiological Sciences',
            'Science Libraries - Physics',
            'Science Libraries - Science Technical Services',
            'Science Libraries - Science and Medicine, History of',
            'Science Libraries - Statistics',
            'Science Libraries - Technology'
        ]
    elif library == 'D\'Angelo Law Library':
        departments = [
            'D\'Angelo Law Library',
            'D\'Angelo Law Library - Administration',
            'D\'Angelo Law Library - Law Technical Services',
            'D\'Angelo Law Library - Law User Services',
            'D\'Angelo Law Library - Law User Services - Access Services',
            'D\'Angelo Law Library - Law User Services - Reference'
        ]
    elif library == 'Eckhart Library':
        departments = []
    elif library == 'Mansueto':
        departments = []
    elif library == 'Regenstein Library':
        departments = [
            'Administration - Communications',
            'Administration - Development',
            'Administration - Director\'s Office',
            'Adminstrative Services - Budget',
            'Adminstrative Services - Building Services',
            'Adminstrative Services - Human Resources',
            'Adminstrative Services - Shipping and Receiving',
            'Collection Services',
            'Collection Services - Preservation',
            'Collection Services - Technical Services',
            'Digital Services',
            'User Services - Access Services - ID & Privileges Office & Entry Control',
            'User Services - Access Services - Regenstein Circulation',
            'User Services - Collection Management and Special Projects - Regenstein Search Services',
            'User Services - Dissertation Office',
            'User Services - Reference, Instruction, and Outreach'
        ]
    elif library == 'Special Collections Research Center':
        departments = [
            'Special Collections Research Center - SCRC Administration',
            'Special Collections Research Center - SCRC Archives and Manuscripts',
            'Special Collections Research Center - SCRC Collection Management',
            'Special Collections Research Center - SCRC Exhibits',
            'Special Collections Research Center - SCRC Rare Books',
            'Special Collections Research Center - SCRC Reader Services'
        ]
    elif library == 'SSA Library':
        departments = []
    else:
        departments = []

    output = []
    for d in departments:
        output.append({
            'directory_unit': DirectoryUnit.objects.get(fullName=d),
            'label': d.split(' - ').pop()
        })
    return sorted(output, key=lambda d: d['label'])

def get_vcards_for_department(department):
    depts = DirectoryUnit.objects.get(fullName=department).get_descendants(True)
    vcards = VCard.objects.filter(unit__in=depts)
    return vcards

def get_staff_pages_for_library(library = None):
    staff_pks = []
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
    if staff_pks:
        staff_pages_all = StaffPage.objects.filter(pk__in=staff_pks).order_by('last_name', 'first_name')
    else:
        staff_pages_all = StaffPage.objects.live().order_by('last_name', 'first_name')
    return staff_pages_all

def units(request):
    def get_unit_info_from_unit_page(unit_page):
        h = ''
        # phone number
        if unit_page.phone_number:
            if unit_page.phone_label:
                h = h + '<em>' + unit_page.phone_label + ':' + '</em> '
            h = h + "<a href='tel:'" + unit_page.phone_number + ">" + unit_page.phone_number + "</a>"
            h = h + '<br/>'

        # fax_number  
        if unit_page.fax_number:
            h = h + 'Fax: ' + unit_page.fax_number + '<br/>'

        # email_label, email
        if unit_page.email:
            if unit_page.email_label:
                h = h + "<a href='mailto:" + unit_page.email + "'>" + unit_page.email_label + "</a><br/>"
            else:
                h = h + "<a href='mailto:" + unit_page.email + "'>" + unit_page.email + "</a><br/>"

        # link_text, link_external
        if unit_page.link_external:
            if unit_page.link_text:
                h = h + "<a href='" + unit_page.link_external + "'>" + unit_page.link_text + "</a><br/>"
            else:
                h = h + "<a href='" + unit_page.link_external + "'>" + unit_page.link_external + "</a><br/>"

        return h

    def get_unit_info(t):
        h = ''

        # intercept this in the future to link to unit pages. 
        if t.name:
            h = h + "<strong>" + t.name + "</strong><br/>"
        if t.unit_page:
            h = h + get_unit_info_from_unit_page(t.unit_page)

        if t.unit_page.directory_unit:
            h = h + t.unit_page.directory_unit.get_parent_library_name() + "<br/>"

        if h:
            h = '<p>' + h + '</p>'
        return h
        
    # hierarchical html. e.g.,
    # <ul>
    #   <li>Administration</li>
    #   <li>Collection Services
    #      <ul>
    #         <li>Administration</li>
    # ...
    def get_html(tree):
        if not tree:
            return ''
        else:
            return "<ul>" + "".join(list(map(lambda t: "<li>" + get_unit_info(t) + get_html(t) + "</li>", tree.children))) + "</ul>"

    # 
    # MAIN
    #

    alphabetical_html = ''
    hierarchical_html = ''
    
    department = request.GET.get('department', None)
    library = request.GET.get('library', None)
    page = request.GET.get('page', 1)
    query = request.GET.get('query', None)
    sort = request.GET.get('sort', 'alphabetical')
    subject = request.GET.get('subject', None)
    view = request.GET.get('view', 'department')

    if view == 'department' and query:
        sort = 'alphabetical'

    # staff pages
    staff_pages_all = []
    staff_pages = []

    if view == 'staff':
        # returns all staff pages if library is None.
        # otherwise, returns staff pages for the given library.
        staff_pages_all = get_staff_pages_for_library(library)

        # departments.
        if department:
            staff_pages_all = staff_pages_all.filter(vcards__in=get_vcards_for_department(department))

        # search staff pages.
        if query:
            staff_pages_all = staff_pages_all.search(query)

        # subjects.
        if subject:
            staff_pages_all = staff_pages_all.filter(staff_subject_placements__in=StaffPageSubjectPlacement.objects.filter(subject=Subject.objects.get(name=subject)))
        
        # add paging.
        paginator = Paginator(staff_pages_all, 50)
        try:
            staff_pages = paginator.page(page)
        except PageNotAnInteger:
            staff_pages = paginator.page(1)
        except EmptyPage:
            staff_pages = paginator.page(paginator.num_pages)

    elif view == 'department':
        hierarchical_units = UnitPage.hierarchical_units()
        hierarchical_html = get_html(hierarchical_units)
        # replace first ul. 
        if len(hierarchical_html) > 4:
            hierarchical_html = "<ul class='directory'>" + hierarchical_html[4:]
    
        # alphabetical units. 
        alphabetical_html = "<table class='table table-striped'>"

        units = UnitPage.objects.filter(display_in_directory=True).extra(select={'lc': 'lower(alphabetical_directory_name)'}).order_by('lc')
        if query:
            units = units.search(query)

        for unit_page in units:
            alphabetical_html = alphabetical_html + '<tr>'
            alphabetical_html = alphabetical_html + '<td><strong>' + unit_page.alphabetical_directory_name + '</strong></td>'
            alphabetical_html = alphabetical_html + '<td>'
            alphabetical_html = alphabetical_html + get_unit_info_from_unit_page(unit_page)
            alphabetical_html = alphabetical_html + '</td>'
            alphabetical_html = alphabetical_html + '<td>'
            alphabetical_html = alphabetical_html + unit_page.directory_unit.get_parent_library_name()
            alphabetical_html = alphabetical_html + '</td>'
            alphabetical_html = alphabetical_html + '</tr>'
        alphabetical_html = alphabetical_html + '</table>'

    return render(request, 'units/unit_index_page.html', {
        'alphabetical_units': alphabetical_html,
        'department': department,
        'departments': get_departments(library),
        'hierarchical_units': hierarchical_html,
        'libraries': ["Regenstein Library", "Crerar Library", "D'Angelo Law Library", "Eckhart Library", "Mansueto", "Special Collections Research Center", "SSA Library"],
        'library': library,
        'query': query,
        'sort': sort,
        'staff_pages': staff_pages,
        'subjects': get_subjects(),
        'subject': subject,
        'view': view,
        'self': {
            'has_right_sidebar': True
        }
    })
