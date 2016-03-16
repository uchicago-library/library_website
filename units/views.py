from django.shortcuts import render
from django.utils.html import escape
from units.models import UnitPage

class Tree(object):
    def __init__(self, name='root', unit_page=None, children=None):
        self.name = name
        self.unit_page = unit_page
        self.children = []
        if children is not None:
            for child in children:
                self.add_child(child)
    def __repr__(self):
        return self.name
    def add_child(self, node):
        assert isinstance(node, Tree)
        self.children.append(node)
    def get_child(self, name):
        c = 0
        while c < len(self.children):
            if self.children[c].name == name:
                return self.children[c]
            c = c + 1
        return None

def units(request):
    # flat units. e.g.,
    # Administration
    # Collection Services
    # Collection Services - Administration
    # ...
    records = []
    for u in UnitPage.objects.filter(display_in_directory=True):
        records.append([u.get_full_name().split(' - '), u])

    # hierarchical units. e.g.,
    # Administration
    # Collection Services
    #    - Administration
    # ...
    hierarchical_units = Tree()
    for record, unit_page in records:
        t = hierarchical_units
        for field in record:
            new_child = t.get_child(field)
            if not new_child:
                new_child = Tree(field, unit_page)
                t.add_child(new_child)
            t = new_child

    # JEJ
    def get_unit_info(tree):
        h = ''
        h = h + tree.name + "<br/>"

        # phone number
        if tree.unit_page.phone_number:
            if tree.unit_page.phone_label:
                h = h + '<em>' + tree.unit_page.phone_label + ':' + '</em> '
            h = h + tree.unit_page.phone_number 
            h = h + '<br/>'

        # fax_number  
        if tree.unit_page.fax_number:
            h = h + 'Fax: ' + tree.unit_page.fax_number + '<br/>'

        # email_label, email
        if tree.unit_page.email:
            if tree.unit_page.email_label:
                h = h + tree.unit_page.email_label + ': '
            h = h + tree.unit_page.email

        # link_text, link_page
        if tree.unit_page.link_page:
            if tree.unit_page.link_text:
                h = h + tree.unit_page.link_text + ': '
            h = h + tree.unit_page.link_page.url
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
    hierarchical_html = get_html(hierarchical_units)

    # alphabetical units. 

    # reverse the breadcrumb trail. 
    r = 0
    while r < len(records):
        records[r][0] = list(reversed(records[r][0]))
        r = r + 1

    # find the shortest way to uniquely describe each unit. 
    def get_shortest_unique_breadcrumb_trail(trails, trail):
        checking_trails = trails
        column = 0
        while True:
            # just in case.
            if column > 10:
                raise RuntimeError
            checking_trails = list(filter(lambda t, trail = trail, column = column: t[0:column] == trail[0:column], checking_trails)) 
            if len(checking_trails) == 1:
                return checking_trails[0][0:column]
            column = column + 1
        # just in case. 
        raise RuntimeError

    alphabetical_records = []
    r = 0
    while r < len(records):
        # jej 
        alphabetical_records.append((get_shortest_unique_breadcrumb_trail(list(map(lambda r: r[0], records)), records[r][0]), records[r]))
        r = r + 1
    alphabetical_records.sort(key=lambda r: r[0])

    # build the html. 
    alphabetical_html = '<table>'
    for r in alphabetical_records:
        alphabetical_html = alphabetical_html + '<tr>'
        alphabetical_html = alphabetical_html + '<td><strong>' + ', '.join(r[0]) + '</strong></td>'
        alphabetical_html = alphabetical_html + '<td>'
    
        alphabetical_html = alphabetical_html + '<td>'
        # phone number
        if r[1][1].phone_number:
            if r[1][1].phone_label:
                alphabetical_html = alphabetical_html + '<em>' + r[1][1].phone_label + ':' + '</em> '
            alphabetical_html = alphabetical_html + r[1][1].phone_number 
            alphabetical_html = alphabetical_html + '<br/>'

        # fax_number  
        if r[1][1].fax_number:
            alphabetical_html = alphabetical_html + 'Fax: ' + r[1][1].fax_number + '<br/>'

        # email_label, email
        if r[1][1].email:
            if r[1][1].email_label:
                alphabetical_html = alphabetical_html + r[1][1].email_label + ': '
            alphabetical_html = alphabetical_html + r[1][1].email

        # link_text, link_page
        if r[1][1].link_page:
            if r[1][1].link_text:
                alphabetical_html = alphabetical_html + r[1][1].link_text + ': '
            alphabetical_html = alphabetical_html + r[1][1].link_page.url

        alphabetical_html = alphabetical_html + '</td>'
        alphabetical_html = alphabetical_html + '</tr>'
    alphabetical_html = alphabetical_html + '</table>'

    return render(request, 'units/unit_index_page.html', {
        'alphabetical_units': alphabetical_html,
        'hierarchical_units': hierarchical_html
    })
