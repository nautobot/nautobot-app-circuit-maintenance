"""Forms for nautobot_circuit_maintenance."""

from django import forms
from nautobot.apps.forms import NautobotBulkEditForm, NautobotFilterForm, NautobotModelForm, TagsBulkEditFormMixin

from nautobot_circuit_maintenance import models


class CircuitMaintenanceForm(NautobotModelForm):  # pylint: disable=too-many-ancestors
    """CircuitMaintenance creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = models.CircuitMaintenance
        fields = [
            "name",
            "description",
        ]


class CircuitMaintenanceBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """CircuitMaintenance bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.CircuitMaintenance.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


class CircuitMaintenanceFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    model = models.CircuitMaintenance
    field_order = ["q", "name"]

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Slug.",
    )
    name = forms.CharField(required=False, label="Name")
