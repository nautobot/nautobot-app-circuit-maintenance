"""Filtering logic for Circuit Maintenance instances."""
import logging

import django_filters
from django.db.models import Q

from nautobot.circuits.models import Circuit, Provider
from nautobot.utilities.filters import BaseFilterSet
from .models import CircuitMaintenance, CircuitImpact, RawNotification, NotificationSource

logger = logging.getLogger(__name__)


class CircuitMaintenanceFilterSet(BaseFilterSet):
    """Filter capabilities for CircuitMaintenance instances."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    provider = django_filters.ModelMultipleChoiceFilter(
        field_name="provider__slug",
        queryset=Provider.objects.all(),
        to_field_name="slug",
        label="Provider (slug)",
        method="search_providers",
    )

    circuit = django_filters.ModelMultipleChoiceFilter(
        queryset=Circuit.objects.all(),
        label="Circuit",
        method="search_circuits",
    )

    start_time = django_filters.DateTimeFilter(field_name="start_time", lookup_expr="gte")
    end_time = django_filters.DateTimeFilter(field_name="end_time", lookup_expr="lte")

    class Meta:
        """Meta class attributes for CircuitMaintenanceFilterSet."""

        model = CircuitMaintenance
        fields = ["name", "status", "ack"]

    def search(self, queryset, name, value):  # pylint: disable=unused-argument, no-self-use
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)

    def search_providers(self, queryset, name, value):  # pylint: disable=unused-argument, no-self-use
        """Perform the filtered search for Provider IDs."""
        if not value:
            return queryset

        return queryset.filter(circuitimpact__circuit__provider__in=value)

    def search_circuits(self, queryset, name, value):  # pylint: disable=unused-argument, no-self-use
        """Perform the filtered search for Circuit IDs."""
        if not value:
            return queryset

        return queryset.filter(circuitimpact__circuit__in=value)


class CircuitImpactFilterSet(BaseFilterSet):
    """Filter capabilities for Circuit Impact."""

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        model = CircuitImpact
        fields = ["id", "maintenance", "circuit", "impact"]


class RawNotificationFilterSet(BaseFilterSet):
    """Filter capabilities for Raw Notification instances."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    since = django_filters.DateTimeFilter(field_name="stamp", lookup_expr="gte")
    provider = django_filters.ModelMultipleChoiceFilter(
        field_name="provider__slug",
        queryset=Provider.objects.all(),
        to_field_name="slug",
        label="Provider (slug)",
    )
    source = django_filters.ModelMultipleChoiceFilter(
        field_name="source__slug",
        queryset=NotificationSource.objects.all(),
        to_field_name="slug",
        label="Notification Source (slug)",
    )

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        model = RawNotification
        fields = ["sender", "parsed"]

    def search(self, queryset, name, value):  # pylint: disable=unused-argument, no-self-use
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(subject__icontains=value)
        return queryset.filter(qs_filter)


class NotificationSourceFilterSet(BaseFilterSet):
    """Filter capabilities for Notification Source."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:
        """Meta class attributes for NotificationSourceFilterSet."""

        model = NotificationSource
        fields = ["name", "slug", "attach_all_providers"]

    def search(self, queryset, name, value):  # pylint: disable=unused-argument, no-self-use
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)
