"""API serializers for nautobot_circuit_maintenance."""

from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin

from nautobot_circuit_maintenance import models


class CircuitMaintenanceSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """CircuitMaintenance Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.CircuitMaintenance
        fields = "__all__"

        # Option for disabling write for certain fields:
        # read_only_fields = []
