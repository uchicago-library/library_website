from django import forms
from django.core.validators import RegexValidator

from group.models import GroupPage
from units.models import UnitPage

from .models import StaffPage


class StaffReportingForm(forms.Form):
    label_text = "Filename"
    filename = forms.CharField(label=label_text, required=True)

    label_text = "Live pages only"
    live = forms.BooleanField(label=label_text, required=False)

    cnetid_choices = [
        (s.cnetid, s.title)
        for s in StaffPage.objects.live().order_by("last_name", "first_name")
    ]
    label_text = "Individual staffperson"
    cnetid = forms.ChoiceField(
        choices=[("", "")] + cnetid_choices, label=label_text, required=False
    )

    department_choices = [
        (u.get_full_name(), u.get_full_name()) for u in UnitPage.objects.live()
    ]
    label_text = "By department"
    department = forms.ChoiceField(
        choices=[("", "")] + department_choices, label=label_text, required=False
    )

    label_text = "By department (including subdepartments)"
    department_and_subdepartments = forms.ChoiceField(
        choices=[("", "")] + department_choices, label=label_text, required=False
    )

    group_choices = [(g.title, g.title) for g in GroupPage.objects.all()]
    label_text = "By group"
    group = forms.ChoiceField(
        choices=[("", "")] + group_choices, label=label_text, required=False
    )

    v = RegexValidator(r"^[0-9]{8}$", "Please enter dates in YYYYMMDD format.")
    label_text = "Latest revision created at YYYYMMDD"
    latest_revision_created_at = forms.CharField(
        label=label_text, required=False, validators=[v]
    )

    label_text = "Supervises students"
    supervises_students = forms.BooleanField(label=label_text, required=False)

    label_text = "Position eliminated"
    position_eliminated = forms.BooleanField(label=label_text, required=False)

    label_text = "Supervisor"
    supervisor_cnetid = forms.ChoiceField(
        choices=[("", "")] + cnetid_choices, label=label_text, required=False
    )

    label_text = "Supervisor override set"
    supervisor_override = forms.BooleanField(label=label_text, required=False)

    position_title_choices = [
        (t, t)
        for t in sorted(
            list(
                set(
                    StaffPage.objects.exclude(position_title=None).values_list(
                        "position_title", flat=True
                    )
                )
            )
        )
    ]
    label_text = "Position title"
    position_title = forms.ChoiceField(
        choices=[("", "")] + position_title_choices, label=label_text, required=False
    )
