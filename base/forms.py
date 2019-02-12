from django import forms
from staff.models import StaffPage

class PageOwnersForm(forms.Form):
    SITES = [
      ('', ''),
      ('Loop', 'Loop'),
      ('Public', 'Public'),
    ]
    l = 'Limit by site'
    site = forms.ChoiceField(choices=SITES, label=l, required=False)

    cnetid_choices = [(s.cnetid, s.title) for s in StaffPage.objects.live().order_by('last_name', 'first_name')]
    l = 'Limit by staff member'
    cnetid = forms.ChoiceField(choices=[('', '')] + cnetid_choices, label=l, required=False)

    ROLES = [
      ('', ''),
      ('page_maintainer', 'Page Maintainer'),
      ('editor', 'Editor'),
      ('content_specialist', 'Content Specialist'),
    ]
    l = 'Limit by role'
    role = forms.ChoiceField(choices=ROLES, label=l, required=False)
