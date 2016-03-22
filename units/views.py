from django.shortcuts import render
from django.utils.html import escape
from units.models import UnitPage

def units(request):
    hierarchical_units = UnitPage.hierarchical_units()

    def get_unit_info(unit_page):

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

        if unit_page.directory_unit:
            h = h + unit_page.directory_unit.get_parent_library_name() + "<br/>"

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
            return "<ul>" + "".join(list(map(lambda t: "<li><strong>" + t.name + "</strong><br/>" + get_unit_info(t.unit_page) + get_html(t) + "</li>", tree.children))) + "</ul>"
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
        alphabetical_html = alphabetical_html + get_unit_info(unit_page)
        alphabetical_html = alphabetical_html + '</td>'
        alphabetical_html = alphabetical_html + '<td>'
        alphabetical_html = alphabetical_html + unit_page.directory_unit.get_parent_library_name()
        alphabetical_html = alphabetical_html + '</td>'
        alphabetical_html = alphabetical_html + '</tr>'
    alphabetical_html = alphabetical_html + '</table>'

    return render(request, 'units/unit_index_page.html', {
        'alphabetical_units': alphabetical_html,
        'hierarchical_units': hierarchical_html
    })
