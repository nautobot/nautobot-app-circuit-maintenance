# TBD: Remove after releasing pylint-nautobot v0.3.0
# https://github.com/nautobot/pylint-nautobot/commit/48efc016fffa0b9df02f61bdaa9c4a0933351d29
# pylint: disable=nb-incorrect-base-class

"""Forms for Circuit Maintenance."""

from django import forms
from nautobot.apps.forms import (
    BootstrapMixin,
    BulkEditNullBooleanSelect,
    DateTimePicker,
    DynamicModelMultipleChoiceField,
    NautobotBulkEditForm,
    NautobotFilterForm,
    NautobotModelForm,
    StaticSelect2,
    StaticSelect2Multiple,
    TagsBulkEditFormMixin,
    add_blank_choice,
)
from nautobot.circuits.models import Circuit, Provider
from nautobot.core.forms.constants import BOOLEAN_WITH_BLANK_CHOICES

from .choices import CircuitMaintenanceStatusChoices
from .models import (
    CircuitImpact,
    CircuitMaintenance,
    Note,
    NotificationSource,
    RawNotification,
)

BLANK_CHOICE = (("", "---------"),)


class CircuitImpactForm(NautobotModelForm):
    """Form for creating new circuit ID info."""

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        """Metaclass attributes for CircuitMaintenanceCircuitImpactAddForm."""

        model = CircuitImpact
        fields = "__all__"
        widgets = {"maintenance": forms.HiddenInput()}


class CircuitImpactBulkEditForm(NautobotBulkEditForm, TagsBulkEditFormMixin):
    """Form for bulk editing Circuit Impact."""

    pk = forms.ModelMultipleChoiceField(queryset=CircuitImpact.objects.all(), widget=forms.MultipleHiddenInput)

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        nullable_fields = ["impact"]


class CircuitImpactFilterForm(NautobotFilterForm):
    """Filter Form for CircuitImpactFilterForm."""

    model = CircuitImpact
    q = forms.CharField(required=False, label="Search")
    maintenance = DynamicModelMultipleChoiceField(
        queryset=CircuitMaintenance.objects.all(),
        to_field_name="pk",
        required=False,
    )
    circuit = DynamicModelMultipleChoiceField(
        queryset=Circuit.objects.all(),
        to_field_name="pk",
        required=False,
    )
    impact = forms.CharField(max_length=50)


class CircuitMaintenanceForm(NautobotModelForm):
    """Filter Form for CircuitMaintenance instances."""

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        """Metaclass attributes for CircuitMaintenanceAddForm."""

        model = CircuitMaintenance
        fields = "__all__"
        widgets = {"start_time": DateTimePicker(), "end_time": DateTimePicker()}


class CircuitMaintenanceFilterForm(NautobotFilterForm):
    """Form for filtering CircuitMaintenance instances."""

    model = CircuitMaintenance

    q = forms.CharField(required=False, label="Search")
    ack = forms.NullBooleanField(required=False, widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES))
    status = forms.MultipleChoiceField(
        choices=CircuitMaintenanceStatusChoices, required=False, widget=StaticSelect2Multiple()
    )
    provider = DynamicModelMultipleChoiceField(
        queryset=Provider.objects.all(),
        to_field_name="pk",
        required=False,
    )
    circuit = DynamicModelMultipleChoiceField(
        queryset=Circuit.objects.all(),
        required=False,
    )
    start_time = forms.DateTimeField(label="Start time after", required=False, widget=DateTimePicker())
    end_time = forms.DateTimeField(label="End time before", required=False, widget=DateTimePicker())


class CircuitMaintenanceBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):
    """Form for bulk editing Circuit Maintenances."""

    pk = forms.ModelMultipleChoiceField(queryset=CircuitMaintenance.objects.all(), widget=forms.MultipleHiddenInput)
    status = forms.ChoiceField(
        required=False, choices=add_blank_choice(CircuitMaintenanceStatusChoices), widget=StaticSelect2
    )
    ack = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect())
    description = forms.CharField(max_length=200, required=False)

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        nullable_fields = ["description"]


class NoteForm(NautobotModelForm):
    """Form for creating new maintenance note."""

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        """Metaclass attributes for NoteForm."""

        model = Note
        fields = "__all__"
        widgets = {"maintenance": forms.HiddenInput()}


class NoteBulkEditForm(NautobotBulkEditForm, TagsBulkEditFormMixin):
    """Form for bulk editing Notes."""

    pk = forms.ModelMultipleChoiceField(queryset=Note.objects.all(), widget=forms.MultipleHiddenInput)
    title = forms.CharField(max_length=200)
    level = forms.CharField(max_length=50, required=False)
    comment = forms.CharField(max_length=200)

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        nullable_fields = ["level"]


class NoteFilterForm(NautobotFilterForm):
    """Filter Form for creating new maintenance note."""

    model = Note
    q = forms.CharField(required=False, label="Search")
    maintenance = DynamicModelMultipleChoiceField(
        queryset=CircuitMaintenance.objects.all(),
        to_field_name="pk",
        required=False,
    )
    title = forms.CharField(max_length=200)
    level = forms.CharField(max_length=50, required=False)
    comment = forms.CharField(max_length=200)


class RawNotificationFilterForm(NautobotFilterForm):
    """Form for filtering Raw Notification instances."""

    model = RawNotification

    q = forms.CharField(required=False, label="Search")
    provider = DynamicModelMultipleChoiceField(queryset=Provider.objects.all(), to_field_name="pk", required=False)
    sender = forms.CharField(required=False)
    source = DynamicModelMultipleChoiceField(
        queryset=NotificationSource.objects.all(), to_field_name="pk", required=False
    )
    parsed = forms.NullBooleanField(required=False, widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES))
    since = forms.DateTimeField(required=False, widget=DateTimePicker())


class NotificationSourceForm(BootstrapMixin, forms.ModelForm):
    """Form for creating new NotificationSource."""

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        """Metaclass attributes for NotificationSourceForm."""

        model = NotificationSource
        fields = ["providers"]


class NotificationSourceBulkEditForm(NautobotBulkEditForm, TagsBulkEditFormMixin):
    """Form for bulk editing NotificationSources."""

    pk = forms.ModelMultipleChoiceField(queryset=NotificationSource.objects.all(), widget=forms.MultipleHiddenInput)

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        nullable_fields = ["providers"]


class NotificationSourceFilterSetForm(BootstrapMixin, forms.ModelForm):
    """Form for filtering Notification Sources."""

    q = forms.CharField(required=False, label="Search")

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        model = NotificationSource
        fields = ["q"]
