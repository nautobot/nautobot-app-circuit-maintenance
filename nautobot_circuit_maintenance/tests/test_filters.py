"""Tests for Circuit Maintenance filtersets, filter forms, and list-view sorting.

Regression coverage for issue #377 (incorrect filters and sort columns on list views).
"""

from django import forms
from nautobot.apps.testing import TestCase
from nautobot.circuits.models import Circuit, CircuitType, Provider
from nautobot.extras.models import Status

from nautobot_circuit_maintenance.choices import CircuitImpactChoices, NoteLevelChoices
from nautobot_circuit_maintenance.filters import (
    CircuitImpactFilterSet,
    CircuitMaintenanceFilterSet,
    NoteFilterSet,
)
from nautobot_circuit_maintenance.forms import (
    CircuitImpactFilterForm,
    NoteFilterForm,
)
from nautobot_circuit_maintenance.models import CircuitImpact, CircuitMaintenance, Note


def _build_circuit_fixtures():
    """Create providers, circuits, maintenances, and impacts shared across filter tests."""
    provider_1 = Provider.objects.create(name="Filter Provider 1")
    provider_2 = Provider.objects.create(name="Filter Provider 2")
    circuit_type = CircuitType.objects.create(name="Filter Circuit Type")
    status = Status.objects.get(name="Active")

    circuit_1 = Circuit.objects.create(
        cid="FILTER-CID-1", provider=provider_1, circuit_type=circuit_type, status=status
    )
    circuit_2 = Circuit.objects.create(
        cid="FILTER-CID-2", provider=provider_2, circuit_type=circuit_type, status=status
    )

    maintenance_1 = CircuitMaintenance.objects.create(
        name="FLT-MAINT-1", start_time="2021-10-04T10:00:00Z", end_time="2021-10-04T12:00:00Z"
    )
    maintenance_2 = CircuitMaintenance.objects.create(
        name="FLT-MAINT-2", start_time="2021-10-05T10:00:00Z", end_time="2021-10-05T12:00:00Z"
    )

    impact_1 = CircuitImpact.objects.create(
        maintenance=maintenance_1, circuit=circuit_1, impact=CircuitImpactChoices.OUTAGE
    )
    impact_2 = CircuitImpact.objects.create(
        maintenance=maintenance_2, circuit=circuit_2, impact=CircuitImpactChoices.NO_IMPACT
    )

    return {
        "provider_1": provider_1,
        "provider_2": provider_2,
        "circuit_1": circuit_1,
        "circuit_2": circuit_2,
        "maintenance_1": maintenance_1,
        "maintenance_2": maintenance_2,
        "impact_1": impact_1,
        "impact_2": impact_2,
    }


class CircuitMaintenanceFilterSetTestCase(TestCase):
    """Filter tests for CircuitMaintenanceFilterSet."""

    queryset = CircuitMaintenance.objects.all()
    filterset = CircuitMaintenanceFilterSet

    @classmethod
    def setUpTestData(cls):
        cls.data = _build_circuit_fixtures()

    def test_provider_filter(self):
        """Filtering maintenances by the related circuit's provider (natural key) resolves and is scoped."""
        params = {"provider": [self.data["provider_1"].name]}
        result = self.filterset(params, self.queryset).qs
        self.assertIn(self.data["maintenance_1"], result)
        self.assertNotIn(self.data["maintenance_2"], result)

    def test_circuit_filter(self):
        """Filtering maintenances by related circuit (cid natural key) resolves and is scoped."""
        params = {"circuit": [self.data["circuit_1"].cid]}
        result = self.filterset(params, self.queryset).qs
        self.assertIn(self.data["maintenance_1"], result)
        self.assertNotIn(self.data["maintenance_2"], result)


class CircuitImpactFilterSetTestCase(TestCase):
    """Filter tests for CircuitImpactFilterSet."""

    queryset = CircuitImpact.objects.all()
    filterset = CircuitImpactFilterSet

    @classmethod
    def setUpTestData(cls):
        cls.data = _build_circuit_fixtures()

    def test_search_filter_present(self):
        """CircuitImpactFilterSet exposes a `q` search filter matching its filter form."""
        self.assertIn("q", self.filterset().filters)

    def test_circuit_filter(self):
        """Filtering impacts by circuit (cid natural key) resolves and is scoped."""
        params = {"circuit": [self.data["circuit_1"].cid]}
        result = self.filterset(params, self.queryset).qs
        self.assertIn(self.data["impact_1"], result)
        self.assertNotIn(self.data["impact_2"], result)

    def test_impact_filter(self):
        """Filtering impacts by impact choice resolves and is scoped."""
        params = {"impact": [CircuitImpactChoices.OUTAGE]}
        result = self.filterset(params, self.queryset).qs
        self.assertIn(self.data["impact_1"], result)
        self.assertNotIn(self.data["impact_2"], result)


class NoteFilterSetTestCase(TestCase):
    """Filter tests for NoteFilterSet."""

    queryset = Note.objects.all()
    filterset = NoteFilterSet

    @classmethod
    def setUpTestData(cls):
        maintenance = CircuitMaintenance.objects.create(
            name="FLT-NOTE-MAINT", start_time="2021-10-04T10:00:00Z", end_time="2021-10-04T12:00:00Z"
        )
        cls.note_info = Note.objects.create(
            maintenance=maintenance, title="Note Info", level=NoteLevelChoices.INFO, comment="info"
        )
        cls.note_warning = Note.objects.create(
            maintenance=maintenance, title="Note Warning", level=NoteLevelChoices.WARNING, comment="warning"
        )

    def test_level_filter(self):
        """Filtering notes by level choice resolves and is scoped."""
        params = {"level": [NoteLevelChoices.WARNING]}
        result = self.filterset(params, self.queryset).qs
        self.assertIn(self.note_warning, result)
        self.assertNotIn(self.note_info, result)


class FilterFormTestCase(TestCase):
    """Tests that filter forms use correct field types and correspond to their filtersets."""

    def test_circuit_impact_impact_is_multiple_choice(self):
        """The impact filter form field is a (non-required) MultipleChoiceField, not free text."""
        field = CircuitImpactFilterForm().fields["impact"]
        self.assertIsInstance(field, forms.MultipleChoiceField)
        self.assertFalse(field.required)

    def test_note_level_is_multiple_choice(self):
        """The Note level filter form field is a (non-required) MultipleChoiceField, not free text."""
        field = NoteFilterForm().fields["level"]
        self.assertIsInstance(field, forms.MultipleChoiceField)
        self.assertFalse(field.required)

    def test_note_filter_form_fields_not_required(self):
        """All Note filter form fields are optional (filter forms must not require fields)."""
        form = NoteFilterForm()
        self.assertFalse(form.fields["title"].required)
        self.assertFalse(form.fields["comment"].required)

    def test_circuit_impact_form_fields_have_matching_filters(self):
        """Every CircuitImpact filter form field maps to a filter on the filterset."""
        filterset_filters = set(CircuitImpactFilterSet().filters)
        for field_name in CircuitImpactFilterForm().fields:
            self.assertIn(
                field_name,
                filterset_filters,
                msg=f"CircuitImpactFilterForm field '{field_name}' has no matching filter on CircuitImpactFilterSet",
            )
