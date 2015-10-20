from django import template
from group.models import GroupMember, GroupPage, GroupIndexPage
from staff.models import StaffPage

register = template.Library()

@register.inclusion_tag('group/tags/group_index.html')
def group_index():
	groupindexpage = GroupIndexPage.objects.live().first()
	return {
		'groups': GroupPage.objects.live().child_of(groupindexpage)
	}

@register.inclusion_tag('group/tags/group_members.html', takes_context=True)
def group_members(context):
	context_group_id = context['self'].id
	staff_ids = []
	for g in GroupMember.objects.filter(group_id=context_group_id).values():
		staff_ids.append(g['staff_id'])
	return {
		'group_members': StaffPage.objects.filter(id__in=staff_ids)
	}

