"""Filtering for nautobot_circuit_maintenance."""

from nautobot.apps.filters import NameSearchFilterSet, NautobotFilterSet

from nautobot_circuit_maintenance import models


class CircuitMaintenanceFilterSet(NautobotFilterSet, NameSearchFilterSet):  # pylint: disable=too-many-ancestors
    """Filter for CircuitMaintenance."""

    class Meta:
        """Meta attributes for filter."""

        model = models.CircuitMaintenance

        # add any fields from the model that you would like to filter your searches by using those
        fields = ["id", "name", "description"]
