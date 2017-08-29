from django import forms
from django.core.validators import RegexValidator
from units.models import UnitPage

class UnitReportingForm(forms.Form):
    l = 'Filename'
    filename = forms.CharField(label=l, required=True)

    l = 'Live pages only'
    live = forms.BooleanField(label=l, required=False)

    l = 'Display in campus directory set'
    display_in_campus_directory = forms.BooleanField(label=l, required=False)

    v = RegexValidator(r'^[0-9]{8}$', 'Please enter dates in YYYYMMDD format.')
    l = 'Latest revision created at'
    latest_revision_created_at = forms.DateField(label=l, required=False, validators=[v])

