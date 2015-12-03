from django import template

# see http://djangosnippets.org/snippets/2093/
from looptags import Loop

register = template.Library()

@register.tag('while')
class WhileNode(template.Node):
    '''Loops over a block as long as a boolean expression is "true".

    For example, to pop each athlete from a list of athletes ``athlete_list``::

        <ul>
        {% while athlete_list %}
            <li>{{ athlete_list.pop.name }}</li>
        {% endwhile %}
        </ul>

    The while loop sets a number of variables available within the loop:

        ==========================  ================================================
        Variable                    Description
        ==========================  ================================================
        ``whileloop.counter``       The current iteration of the loop (1-indexed)
        ``whileloop.counter0``      The current iteration of the loop (0-indexed)
                                    loop (0-indexed)
        ``whileloop.first``         True if this is the first time through the loop
        ``whileloop.parentloop``    For nested loops, this is the loop "above" the
                                    current one
        ==========================  ================================================

    You can also ``continue`` or ``break`` from the loop by using the respective
    filters on the ``whileloop`` variable::

        <ul>
        {% while athlete_list %}
            {% with athlete_list.pop.name as athlete %}
                {% if athlete == 'Woods' %}
                    {{ whileloop|continue }}
                {% endif %}
                <li>{{ athlete }}</li>
                {% if athlete == 'Pele' %}
                    {{ whileloop|break }}
                {% endif %}
            {% endwith %}
        {% endwhile %}
        </ul>
    '''

    child_nodelists = ('nodelist_loop',)

    def __init__(self, parser, token):
        bits = token.split_contents()[1:]
        self.var = template.defaulttags.TemplateIfParser(parser, bits).parse()
        self.nodelist_loop = parser.parse(('endwhile',))
        parser.delete_first_token()

    def __rer__(self):
        return "<While node>"

    def __iter__(self):
        return self.nodelist_loop

    def render(self, context):
        loop = Loop('whileloop', context, self.nodelist_loop)
        eval_var = self.var.eval
        while True:
            try:
                if not eval_var(context):
                    break
            except template.VariableDoesNotExist:
                break
            if loop.next() is loop.BREAK:
                break
        return loop.render(close=True)
