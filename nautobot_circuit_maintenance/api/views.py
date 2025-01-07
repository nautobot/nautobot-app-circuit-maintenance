"""API views for nautobot_circuit_maintenance."""

from nautobot.apps.api import NautobotModelViewSet

from nautobot_circuit_maintenance import filters, models
from nautobot_circuit_maintenance.api import serializers


class CircuitMaintenanceViewSet(NautobotModelViewSet):  # pylint: disable=too-many-ancestors
    """CircuitMaintenance viewset."""

    queryset = models.CircuitMaintenance.objects.all()
    serializer_class = serializers.CircuitMaintenanceSerializer
    filterset_class = filters.CircuitMaintenanceFilterSet

    # Option for modifying the default HTTP methods:
    # http_method_names = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]
