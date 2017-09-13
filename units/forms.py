from django import forms
from django.core.validators import RegexValidator
from units.models import UnitPage
from wagtail.wagtailadmin.widgets import AdminDateInput
from wagtail.wagtailcore.blocks import DateBlock

class UnitReportingForm(forms.Form):
    l = 'Filename'
    filename = forms.CharField(label=l, required=True)

    l = 'Email to'
    # a PageChooser would be cooler.
    email_to = forms.EmailField(label=l, required=True)

    l = 'Live pages only'
    live = forms.BooleanField(label=l, required=False)

    l = 'Display in campus directory set'
    display_in_campus_directory = forms.BooleanField(label=l, required=False)

    v = RegexValidator(r'^[0-9]{8}$', 'Please enter dates in YYYYMMDD format.')
    l = 'Latest revision created at YYYYMMDD'
    latest_revision_created_at = forms.CharField(label=l, required=False, validators=[v], widget=AdminDateInput())
