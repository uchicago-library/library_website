from django.shortcuts import render
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
        

def units(request):
    # flat units. 
    records = []
    for u in UnitPage.objects.filter(display_in_directory=True):
        fields = u.directory_unit.fullName.split(' - ')
        if u.contact_point_title:
            fields.append(u.contact_point_title)
        records.append(fields)

    # hierarchical units.
    hierarchical_units = Tree()
    for fields in records:
        t = hierarchical_units
        for field in fields:
            if not field in t.children:
                new_child = Tree(field)
                t.add_child(new_child)
                t = new_child

    # hierarchical html.
    def get_html(tree):
        if not tree:
            return ''
        else:
            return "<ul>" + "".join(list(map(lambda t: "<li>" + t.name + get_html(t) + "</li>", tree.children))) + "</ul>"
    units_html = get_html(hierarchical_units)

    # make a hierarchical list- for each thing in the list above,
    # check to see if each piece exists, if not create it. 

    return render(request, 'units/unit_index_page.html', {
        'hierarchical_units': units_html
    })
