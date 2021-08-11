"""Filtering logic for Circuit Maintenance instances."""
import logging

import django_filters
from django.db.models import Q

from nautobot.utilities.filters import BaseFilterSet
from .models import CircuitMaintenance, CircuitImpact, RawNotification, NotificationSource

logger = logging.getLogger(__name__)


class CircuitMaintenanceFilterSet(BaseFilterSet):
    """Filter capabilities for CircuitMaintenance instances."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    # TODO: user nautobot.utilities.filters.MultiValueCharFilter
    provider = django_filters.CharFilter(
        method="search_providers",
        label="provider",
    )

    # TODO: user nautobot.utilities.filters.MultiValueCharFilter
    circuit = django_filters.CharFilter(
        method="search_circuits",
        label="circuit",
    )

    start_time = django_filters.DateTimeFilter(field_name="start_time", lookup_expr="gte")
    end_time = django_filters.DateTimeFilter(field_name="end_time", lookup_expr="lte")

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
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
        if not value or not value.strip():
            return queryset

        matching_maintenances = CircuitImpact.objects.filter(circuit__provider__id=value).values_list("maintenance")
        return queryset.filter(id__in=matching_maintenances)

    def search_circuits(self, queryset, name, value):  # pylint: disable=unused-argument, no-self-use
        """Perform the filtered search for Circuit IDs."""
        if not value or not value.strip():
            return queryset

        matching_maintenances = CircuitImpact.objects.filter(circuit__id=value).values_list("maintenance")
        return queryset.filter(id__in=matching_maintenances)


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

    since = django_filters.DateTimeFilter(field_name="date", lookup_expr="gte")

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        model = RawNotification
        fields = ["provider", "sender", "source", "parsed"]

    def search(self, queryset, name, value):  # pylint: disable=unused-argument, no-self-use
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(subject__icontains=value)
        return queryset.filter(qs_filter)


class NotificationSourceFilterSet(BaseFilterSet):
    """Filter capabilities for Notifiaction Source."""

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        model = NotificationSource
        fields = ["name", "slug", "attach_all_providers"]

    def search(self, queryset, name, value):  # pylint: disable=unused-argument, no-self-use
        """Perform the filtered search."""
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value)
        return queryset.filter(qs_filter)
