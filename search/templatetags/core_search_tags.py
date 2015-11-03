from django import template
import staff

register = template.Library()

@register.simple_tag(takes_context=True)
def pagetype(context, page):
	if type(page.specific_class()) is staff.models.StaffIndexPage:
		return 'Staff Index Page'
	elif type(page.specific_class()) is staff.models.StaffPage:
		return 'Staff Page'
	else:
		return 'Unknown page type'


