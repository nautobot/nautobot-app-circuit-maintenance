"""Filtering logic for Circuit Maintenance instances."""

import logging

import django_filters
from nautobot.apps.filters import NaturalKeyOrPKMultipleChoiceFilter, NautobotFilterSet, SearchFilter
from nautobot.circuits.models import Circuit, Provider

from .models import CircuitImpact, CircuitMaintenance, Note, NotificationSource, ParsedNotification, RawNotification

logger = logging.getLogger(__name__)


class CircuitMaintenanceFilterSet(NameSearchFilterSet, NautobotFilterSet):  # pylint: disable=too-many-ancestors
    """Filter for CircuitMaintenance."""

    class Meta:
        """Meta class attributes for CircuitMaintenanceFilterSet."""

        model = CircuitMaintenance
        fields = "__all__"

        # add any fields from the model that you would like to filter your searches by using those
        fields = "__all__"
