"""Forms for Circuit Maintenance."""
from django import forms
from django_filters.widgets import BooleanWidget
from nautobot.circuits.models import Circuit, Provider
from nautobot.utilities.forms import (
    BootstrapMixin,
    DateTimePicker,
)
from nautobot.extras.forms import (
    AddRemoveTagsForm,
    CustomFieldBulkEditForm,
    CustomFieldFilterForm,
    CustomFieldModelForm,
    CustomFieldModelCSVForm,
    RelationshipModelForm,
)
from .models import (
    CircuitImpact,
    CircuitMaintenance,
    Note,
    EmailSettings,
    RawNotification,
)


BLANK_CHOICE = (("", "---------"),)


class CircuitImpactForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    """Form for creating new circuit ID info."""

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        """Metaclass attributes for CircuitMaintenanceCircuitImpactAddForm."""

        model = CircuitImpact
        fields = ["maintenance", "circuit", "impact"]
        widgets = {"maintenance": forms.HiddenInput()}


class CircuitImpactCSVForm(CustomFieldModelCSVForm):
    """Form for creating bulk Circuit Impact."""

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        model = CircuitImpact
        fields = CircuitImpact.csv_headers


class CircuitImpactBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    """Form for bulk editing Circuit Impact."""

    pk = forms.ModelMultipleChoiceField(queryset=CircuitImpact.objects.all(), widget=forms.MultipleHiddenInput)

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        nullable_fields = ["impact"]


class CircuitMaintenanceForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    """Filter Form for CircuitMaintenance instances."""

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        """Metaclass attributes for CircuitMaintenanceAddForm."""

        model = CircuitMaintenance
        fields = ["name", "start_time", "end_time", "description", "status", "ack"]
        widgets = {"start_time": DateTimePicker(), "end_time": DateTimePicker()}


class CircuitMaintenanceFilterForm(BootstrapMixin, CustomFieldFilterForm):
    """Form for filtering CircuitMaintenance instances."""

    model = CircuitMaintenance

    provider = forms.ModelChoiceField(
        queryset=Provider.objects.all(),
        required=False,
    )
    circuit = forms.ModelChoiceField(
        queryset=Circuit.objects.all(),
        required=False,
    )
    start_time = forms.DateTimeField(required=False, widget=DateTimePicker())
    end_time = forms.DateTimeField(required=False, widget=DateTimePicker())
    ack = forms.BooleanField(required=False, widget=BooleanWidget())

    q = forms.CharField(required=False, label="Search")


class CircuitMaintenanceCSVForm(CustomFieldModelCSVForm):
    """Form for creating bulk Circuit Maintenances."""

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        model = CircuitMaintenance
        fields = CircuitMaintenance.csv_headers


class CircuitMaintenanceBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    """Form for bulk editing Circuit Maintenances."""

    pk = forms.ModelMultipleChoiceField(queryset=CircuitMaintenance.objects.all(), widget=forms.MultipleHiddenInput)
    status = forms.CharField(max_length=200, required=False)
    ack = forms.BooleanField(required=False, widget=BooleanWidget())
    description = forms.CharField(max_length=200, required=False)

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        nullable_fields = ["status", "ack", "description"]


class NoteForm(BootstrapMixin, CustomFieldModelForm, RelationshipModelForm):
    """Form for creating new maintenance note."""

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        """Metaclass attributes for NoteForm."""

        model = Note
        fields = ["maintenance", "title", "comment", "level"]
        widgets = {"maintenance": forms.HiddenInput()}


class NoteBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    """Form for bulk editing Notes."""

    pk = forms.ModelMultipleChoiceField(queryset=Note.objects.all(), widget=forms.MultipleHiddenInput)
    title = forms.CharField(max_length=200)
    level = forms.CharField(max_length=50, required=False)
    comment = forms.CharField(max_length=200)

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        nullable_fields = ["level", "date"]


class NoteCSVForm(CustomFieldModelCSVForm):
    """Form for creating bulk Notes."""

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        model = Note
        fields = Note.csv_headers


class RawNotificationFilterSetForm(BootstrapMixin, CustomFieldFilterForm):
    """Form for filtering Raw Notification instances."""

    model = RawNotification

    q = forms.CharField(required=False, label="Search")
    sender = forms.CharField(required=False)
    parsed = forms.BooleanField(required=False, widget=BooleanWidget())
    since = forms.DateTimeField(required=False, widget=DateTimePicker())


class EmailSettingsForm(BootstrapMixin, forms.ModelForm):
    """Form for creating new maintenance email source."""

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        """Metaclass attributes for EmailSettingsmodel_form = forms.EmailSettingsForm."""

        model = EmailSettings
        fields = ["email", "_password", "url", "server_type", "providers"]
        widgets = {"_password": forms.PasswordInput()}


class EmailSettingsCSVForm(CustomFieldModelCSVForm):
    """Form for creating bulk EmailSettings."""

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        model = EmailSettings
        fields = EmailSettings.csv_headers


class EmailSettingsBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    """Form for bulk editing Notes."""

    pk = forms.ModelMultipleChoiceField(queryset=Note.objects.all(), widget=forms.MultipleHiddenInput)

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        nullable_fields = ["server_type", "providers"]


class EmailSettingsFilterSetForm(BootstrapMixin, forms.ModelForm):
    """Form for filtering CircuitMaintenance settings."""

    q = forms.CharField(required=False, label="Search")
    url = forms.CharField(required=False)

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        model = EmailSettings
        fields = ["q", "url", "server_type"]
