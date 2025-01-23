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


class ParsedNotificationSerializer(NautobotModelSerializer):
    """Serializer for API."""

    class Meta:
        """Meta class for ParsedNotificationSerializer."""

        model = models.ParsedNotification
        fields = "__all__"


class RawNotificationSerializer(NautobotModelSerializer):
    """Serializer for API."""

    class Meta:
        """Meta class for RawNotificationSerializer."""

        model = models.RawNotification
        fields = "__all__"


class NoteSerializer(NautobotModelSerializer):
    """Serializer for API."""

    class Meta:
        """Meta class for MaintenanceNoteSerializer."""

        model = models.Note
        fields = "__all__"


class NotificationSourceSerializer(NautobotModelSerializer):
    """Serializer for NotificationSource records."""

    class Meta:
        """Meta class for NotificationSourceSerializer."""

        model = models.NotificationSource
        fields = "__all__"


class CircuitImpactSerializer(NautobotModelSerializer):
    """Serializer for API."""

    class Meta:
        """Meta class for CircuitImpactSerializer."""

        model = models.CircuitImpact
        fields = "__all__"
