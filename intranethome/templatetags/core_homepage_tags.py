from django import template
from group.models import GroupMember, GroupPage, GroupIndexPage
from intranethome.models import IntranetHomePage
from news.models import NewsPage
from staff.models import StaffPage

register = template.Library()

@register.inclusion_tag('intranethome/tags/top_stories.html')
def top_stories():
	return {
		'latest_stories': NewsPage.objects.live().order_by('-latest_revision_created_at')
	}


