from django import forms
from django.core.validators import RegexValidator
from .models import POSITION_STATUS, StaffPage
from units.models import UnitPage

class StaffReportingForm(forms.Form):
    l = 'Filename'
    filename = forms.CharField(label=l, required=True)

    l = 'Live pages only'
    live = forms.BooleanField(label=l, required=False)

    cnetid_choices = [(s.cnetid, s.title) for s in StaffPage.objects.all().order_by('last_name', 'first_name')]
    l = 'Invidual staffperson'
    cnetid = forms.ChoiceField(choices=[('', '')] + cnetid_choices, label=l, required=False)

    department_choices = [(u.get_full_name(), u.get_full_name()) for u in UnitPage.objects.live()]
    l = 'By department'
    department = forms.ChoiceField(choices=[('', '')] + department_choices, label=l, required=False)

    l = 'By department (including subdepartments)'
    department_and_subdepartments = forms.ChoiceField(choices=[('', '')] + department_choices, label=l, required=False)

    v = RegexValidator(r'^[0-9]{8}$', 'Please enter dates in YYYYMMDD format.')
    l = 'Latest revision created at YYYYMMDD'
    latest_revision_created_at = forms.CharField(label=l, required=False, validators=[v])

    l = 'Supervises students'
    supervises_students = forms.BooleanField(label=l, required=False)

    l = 'Position status'
    position_status = forms.ChoiceField(choices=[('', '')] + list(POSITION_STATUS), label=l, required=False)

    l = 'Supervisor'
    supervisor_cnetid = forms.ChoiceField(choices=[('', '')] + cnetid_choices, label=l, required=False)

    l = 'Supervisor override set'
    supervisor_override = forms.BooleanField(label=l, required=False)

    position_title_choices = [(t, t) for t in sorted(list(set(StaffPage.objects.exclude(position_title=None).values_list('position_title', flat=True))))] 
    l = 'Position title'
    position_title = forms.ChoiceField(choices=[('', '')] + position_title_choices, label=l, required=False)
    
