from django import forms
from .models import POSITION_STATUS, StaffPage
from units.models import UnitPage

class StaffReportingForm(forms.Form):
    l = 'Filename'
    filename = forms.CharField(label=l, required=True)

    l = 'All pages or live pages?'
    all_or_live = forms.ChoiceField(choices=[('all', 'All staff pages'), ('live', 'Published (live) staff pages only')], label=l, widget=forms.RadioSelect())

    cnetid_choices = [(s.cnetid, s.title) for s in StaffPage.objects.all().order_by('last_name', 'first_name')]
    l = 'Invidual staffperson'
    cnetid = forms.ChoiceField(choices=[('', '')] + cnetid_choices, label=l, required=False)

    department_choices = [(u.get_full_name(), u.get_full_name()) for u in UnitPage.objects.live()]
    l = 'By department'
    department = forms.ChoiceField(choices=[('', '')] + department_choices, label=l, required=False)

    l = 'By department (including subdepartments)'
    department_and_subdepartments = forms.ChoiceField(choices=[('', '')] + department_choices, label=l, required=False)

    l = 'Modified since'
    modified_since = forms.DateField(label=l, required=False)

    l = 'Supervises students'
    supervises_students = forms.DateField(label=l, required=False)

    l = 'Position status'
    position_status = forms.ChoiceField(choices=[('', '')] + list(POSITION_STATUS), label=l, required=False)

    l = 'Superised by'
    supervisor_cnetid = forms.ChoiceField(choices=[('', '')] + cnetid_choices, label=l, required=False)

    l = 'With supervisor override set'
    supervisor_override_set = forms.BooleanField(label=l, required=False)

    title_choices = [(t, t) for t in sorted(list(set(StaffPage.objects.exclude(position_title=None).values_list('position_title', flat=True))))] 
    l = 'Title'
    title = forms.ChoiceField(choices=[('', '')] + title_choices, label=l, required=False)
    
