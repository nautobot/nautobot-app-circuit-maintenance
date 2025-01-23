"""Filtering logic for Circuit Maintenance instances."""

import logging

import django_filters
from nautobot.apps.filters import NaturalKeyOrPKMultipleChoiceFilter, NautobotFilterSet, SearchFilter
from nautobot.circuits.models import Circuit, Provider

from .models import CircuitImpact, CircuitMaintenance, Note, NotificationSource, ParsedNotification, RawNotification

logger = logging.getLogger(__name__)


class CircuitMaintenanceFilterSet(NautobotFilterSet):
    """Filter capabilities for CircuitMaintenance instances."""

    q = SearchFilter(
        filter_predicates={"name": "icontains"},
    )

    provider = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="provider",
        queryset=Provider.objects.all(),
        to_field_name="name",
        label="Provider",
    )

    circuit = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="circuit",
        queryset=Circuit.objects.all(),
        label="Circuit",
    )

    start_time = django_filters.DateTimeFilter(field_name="start_time", lookup_expr="gte")
    end_time = django_filters.DateTimeFilter(field_name="end_time", lookup_expr="lte")

    class Meta:
        """Meta class attributes for CircuitMaintenanceFilterSet."""

        model = CircuitMaintenance
        fields = "__all__"


class CircuitImpactFilterSet(NautobotFilterSet):
    """Filter capabilities for CircuitImpact instances."""

    maintenance = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="maintenance",
        queryset=CircuitMaintenance.objects.all(),
        to_field_name="name",
        label="CircuitMaintenance",
    )

    circuit = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="circuit",
        queryset=Circuit.objects.all(),
        label="Circuit",
    )

    class Meta:
        """Meta class attributes for CircuitImpactFilterSet."""

        model = CircuitImpact
        fields = "__all__"


class NoteFilterSet(NautobotFilterSet):
    """Filter capabilities for Note instances."""

    q = SearchFilter(
        filter_predicates={"title": "icontains"},
    )

    maintenance = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="maintenance",
        queryset=CircuitMaintenance.objects.all(),
        to_field_name="name",
        label="CircuitMaintenance",
    )

    class Meta:
        """Meta class attributes for NoteFilterSet."""

        model = Note
        fields = "__all__"


class RawNotificationFilterSet(NautobotFilterSet):
    """Filter capabilities for Raw Notification instances."""

    q = SearchFilter(
        filter_predicates={"subject": "icontains"},
    )

    since = django_filters.DateTimeFilter(field_name="stamp", lookup_expr="gte")

    provider = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="provider",
        queryset=Provider.objects.all(),
        to_field_name="name",
        label="Provider",
    )

    source = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="source",
        queryset=NotificationSource.objects.all(),
        to_field_name="name",
        label="Notification Source",
    )

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        model = RawNotification
        exclude = ["raw"]


class ParsedNotificationFilterSet(NautobotFilterSet):
    """Filter capabilities for Notification Source."""

    q = SearchFilter(
        filter_predicates={"raw_notification": "icontains"},
    )

    maintenance = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="maintenance",
        queryset=CircuitMaintenance.objects.all(),
        to_field_name="name",
        label="CircuitMaintenance",
    )

    class Meta:
        """Meta class attributes for ParsedNotificationFilterSet."""

        model = ParsedNotification
        fields = "__all__"


class NotificationSourceFilterSet(NautobotFilterSet):
    """Filter capabilities for Notification Source."""

    q = SearchFilter(
        filter_predicates={"name": "icontains"},
    )

    class Meta:
        """Meta class attributes for NotificationSourceFilterSet."""

        model = NotificationSource
        exclude = ["_token"]
