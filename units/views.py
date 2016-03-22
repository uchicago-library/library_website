from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.utils.html import escape
from staff.models import StaffPage
from units.models import UnitPage

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
    
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort', 'alphabetical')
    view = request.GET.get('view', 'department')

    # staff pages
    staff_pages_all = StaffPage.objects.live().order_by('last_name', 'first_name')
    staff_pages = []

    paginator = Paginator(staff_pages_all, 50)
    try:
        staff_pages = paginator.page(page)
    except PageNotAnInteger:
        staff_pages = paginator.page(1)
    except EmptyPage:
        staff_pages = paginator.page(paginator.num_pages)
    
    hierarchical_units = UnitPage.hierarchical_units()
    hierarchical_html = get_html(hierarchical_units)
    # replace first ul. 
    if len(hierarchical_html) > 4:
        hierarchical_html = "<ul class='directory'>" + hierarchical_html[4:]

    # alphabetical units. 
    alphabetical_html = "<table class='table table-striped'>"
    for unit_page in UnitPage.objects.filter(display_in_directory=True).extra(select={'lc': 'lower(alphabetical_directory_name)'}).order_by('lc'):
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
        'hierarchical_units': hierarchical_html,
        'sort': sort,
        'staff_pages': staff_pages,
        'view': view
    })
