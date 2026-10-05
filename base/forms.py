from django import forms

from staff.models import StaffPage


class PageOwnersForm(forms.Form):
    SITES = [
        ("", ""),
        ("Loop", "Loop"),
        ("Public", "Public"),
    ]
    label = "Limit by site"
    site = forms.ChoiceField(choices=SITES, label=label, required=False)

    cnetid_choices = [
        (s.cnetid, s.title)
        for s in StaffPage.objects.all().order_by("last_name", "first_name")
    ]
    label = "Limit by staff member"
    cnetid = forms.ChoiceField(
        choices=[("", "")] + cnetid_choices, label=label, required=False
    )

    ROLES = [
        ("", ""),
        ("page_maintainer", "Page Maintainer"),
        ("editor", "Editor"),
        ("content_specialist", "Content Specialist"),
    ]
    label = "Limit by role"
    role = forms.ChoiceField(choices=ROLES, label=label, required=False)
