from django.shortcuts import render
from django.utils.html import escape
from units.models import UnitPage

class Tree(object):
    def __init__(self, name='root', children=None):
        self.name = name
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
        fields = u.directory_unit.fullName.split(' - ')
        if u.contact_point_title:
            fields.append(u.contact_point_title)
        records.append(fields)

    # hierarchical units. e.g.,
    # Administration
    # Collection Services
    #    - Administration
    # ...
    hierarchical_units = Tree()
    for record in records:
        t = hierarchical_units
        for field in record:
            new_child = t.get_child(field)
            if not new_child:
                new_child = Tree(field)
                t.add_child(new_child)
            t = new_child

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
            return "<ul>" + "".join(list(map(lambda t: "<li>" + escape(t.name) + get_html(t) + "</li>", tree.children))) + "</ul>"
    hierarchical_html = get_html(hierarchical_units)

    # alphabetical units. 

    # reverse the breadcrumb trail. 
    r = 0
    while r < len(records):
        records[r] = list(reversed(records[r]))
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
        alphabetical_records.append((get_shortest_unique_breadcrumb_trail(records, records[r]), records[r]))
        r = r + 1
    alphabetical_records.sort(key=lambda r: r[0])

    # build the html. 
    alphabetical_html = '<table>'
    for r in alphabetical_records:
        alphabetical_html = alphabetical_html + '<tr>'
        alphabetical_html = alphabetical_html + '<td><strong>' + ', '.join(r[0]) + '</strong></td>'
        alphabetical_html = alphabetical_html + '<td>'
        # phone_label, phone_number
        # fax_number  
        # email_label, email
        # link_text, link_page
        alphabetical_html = alphabetical_html + '</tr>'
    alphabetical_html = alphabetical_html + '</table>'

    return render(request, 'units/unit_index_page.html', {
        'alphabetical_units': alphabetical_html,
        'hierarchical_units': hierarchical_html
    })
