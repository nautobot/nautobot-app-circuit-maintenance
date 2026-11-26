"""Tests for Circuit Maintenance filtersets and filter forms.

Regression coverage for issue #377 (incorrect filters on list views).
"""

from django import forms
from nautobot.apps.testing import FilterTestCases, TestCase
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


def _create_maintenances(count):
    """Create `count` maintenances with distinct names and start times."""
    return [
        CircuitMaintenance.objects.create(
            name=f"FLT-MAINT-{i}",
            start_time=f"2021-10-0{i}T10:00:00Z",
            end_time=f"2021-10-0{i}T12:00:00Z",
        )
        for i in range(1, count + 1)
    ]


def _build_circuit_fixtures():
    """Create providers, circuits, maintenances, and impacts shared across filter tests.

    Provider 1 owns two circuits that are both impacted by the first maintenance, so filtering maintenances by
    that provider traverses two `CircuitImpact` rows for the same maintenance.
    """
    providers = [Provider.objects.create(name=f"Filter Provider {i}") for i in range(1, 4)]
    circuit_type = CircuitType.objects.create(name="Filter Circuit Type")
    status = Status.objects.get(name="Active")
    circuits = [
        Circuit.objects.create(cid=f"FILTER-CID-{i}", provider=provider, circuit_type=circuit_type, status=status)
        for i, provider in enumerate([providers[0], providers[0], providers[1], providers[2]], start=1)
    ]
    maintenances = _create_maintenances(4)
    for maintenance, circuit, impact in [
        (maintenances[0], circuits[0], CircuitImpactChoices.OUTAGE),
        (maintenances[0], circuits[1], CircuitImpactChoices.DEGRADED),
        (maintenances[1], circuits[2], CircuitImpactChoices.NO_IMPACT),
        (maintenances[2], circuits[3], CircuitImpactChoices.REDUCED_REDUNDANCY),
        (maintenances[3], circuits[0], CircuitImpactChoices.OUTAGE),
    ]:
        CircuitImpact.objects.create(maintenance=maintenance, circuit=circuit, impact=impact)


class CircuitMaintenanceFilterSetTestCase(FilterTestCases.FilterTestCase):
    """Filter tests for CircuitMaintenanceFilterSet."""

    queryset = CircuitMaintenance.objects.all()
    filterset = CircuitMaintenanceFilterSet
    generic_filter_tests = (
        ["circuit", "circuitimpact__circuit__cid"],
        ["circuit", "circuitimpact__circuit__id"],
        ["provider", "circuitimpact__circuit__provider__name"],
        ["provider", "circuitimpact__circuit__provider__id"],
    )

    @classmethod
    def setUpTestData(cls):
        _build_circuit_fixtures()


class CircuitImpactFilterSetTestCase(FilterTestCases.FilterTestCase):
    """Filter tests for CircuitImpactFilterSet."""

    queryset = CircuitImpact.objects.all()
    filterset = CircuitImpactFilterSet
    generic_filter_tests = (
        ["circuit", "circuit__cid"],
        ["circuit", "circuit__id"],
        ["maintenance", "maintenance__name"],
        ["maintenance", "maintenance__id"],
        ["impact"],
    )

    @classmethod
    def setUpTestData(cls):
        _build_circuit_fixtures()


class NoteFilterSetTestCase(FilterTestCases.FilterTestCase):
    """Filter tests for NoteFilterSet."""

    queryset = Note.objects.all()
    filterset = NoteFilterSet
    generic_filter_tests = (
        ["maintenance", "maintenance__name"],
        ["maintenance", "maintenance__id"],
    )

    @classmethod
    def setUpTestData(cls):
        maintenances = _create_maintenances(3)
        for maintenance, title, level in [
            (maintenances[0], "Note Info", NoteLevelChoices.INFO),
            (maintenances[1], "Note Warning", NoteLevelChoices.WARNING),
            (maintenances[2], "Note Info 2", NoteLevelChoices.INFO),
        ]:
            Note.objects.create(maintenance=maintenance, title=title, level=level, comment=title.lower())

    def test_level_filter(self):
        """Filtering notes by level choice resolves and is scoped.

        `NoteLevelChoices` has only two values, too few for `generic_filter_tests`, which needs a subset of at
        least two values that still leaves a row unmatched.
        """
        params = {"level": [NoteLevelChoices.WARNING]}
        self.assertQuerySetEqualAndNotEmpty(
            self.filterset(params, self.queryset).qs, self.queryset.filter(level=NoteLevelChoices.WARNING)
        )


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
