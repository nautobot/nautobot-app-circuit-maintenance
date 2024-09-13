"""Filtering logic for Circuit Maintenance instances."""

import logging

import django_filters
from django.db.models import Q
from nautobot.circuits.models import Circuit, Provider
from nautobot.core.filters import NaturalKeyOrPKMultipleChoiceFilter
from nautobot.extras.filters import NautobotFilterSet

from .models import CircuitImpact, CircuitMaintenance, NotificationSource, ParsedNotification, RawNotification

logger = logging.getLogger(__name__)


class CircuitMaintenanceFilterSet(NautobotFilterSet):
    """Filter capabilities for CircuitMaintenance instances."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
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
        fields = '__all__'

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)


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
        fields = '__all__'


class RawNotificationFilterSet(NautobotFilterSet):
    """Filter capabilities for Raw Notification instances."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
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

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(subject__icontains=value)
        return queryset.filter(qs_filter)


class ParsedNotificationFilterSet(NautobotFilterSet):
    """Filter capabilities for Notification Source."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
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
        fields = '__all__'

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(raw_notification__icontains=value)
        return queryset.filter(qs_filter)


class NotificationSourceFilterSet(NautobotFilterSet):
    """Filter capabilities for Notification Source."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        """Meta class attributes for NotificationSourceFilterSet."""

        model = NotificationSource
        exclude = ["_token"]

    def search(self, queryset, name, value):  # pylint: disable=unused-argument
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)
