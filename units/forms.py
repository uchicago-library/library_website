from django import forms
from django.core.validators import RegexValidator
from wagtail.admin.widgets import AdminDateInput


class UnitReportingForm(forms.Form):
    label_text = "Filename"
    filename = forms.CharField(label=label_text, required=True)

    label_text = "Live pages only"
    live = forms.BooleanField(label=label_text, required=False)

    label_text = "Display in campus directory set"
    display_in_campus_directory = forms.BooleanField(label=label_text, required=False)

    v = RegexValidator(r"^[0-9]{8}$", "Please enter dates in YYYYMMDD format.")
    label_text = "Latest revision created at YYYYMMDD"
    latest_revision_created_at = forms.CharField(
        label=label_text, required=False, validators=[v], widget=AdminDateInput()
    )
