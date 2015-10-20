from django import template
from group.models import GroupMember, GroupPage
from staff.models import StaffPage

register = template.Library()

@register.inclusion_tag('staff/tags/staff_listing.html')
def staff_listing():
	return {
		'staff_listing': StaffPage.objects.live().order_by('display_name')
	}

@register.inclusion_tag('staff/tags/staff_groups.html', takes_context=True)
def staff_groups(context):
	context_staff_id = context['self'].id
	group_ids = []
	for g in GroupMember.objects.filter(staff_id=context_staff_id).values():
		group_ids.append(g['group_id'])
	return {
		'staff_groups': GroupPage.objects.filter(id__in=group_ids)
	}

