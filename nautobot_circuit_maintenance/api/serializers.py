"""Serializer for Circuit Maintenance API."""
from nautobot.core.api.serializers import NautobotModelSerializer
from nautobot_circuit_maintenance.models import (
    CircuitImpact,
    CircuitMaintenance,
    Note,
    NotificationSource,
    ParsedNotification,
    RawNotification,
)


class CircuitMaintenanceSerializer(NautobotModelSerializer):
    """Serializer for API."""

    class Meta:
        """Meta class for MaintenanceSerializer."""

        model = CircuitMaintenance
        fields = "__all__"


class ParsedNotificationSerializer(NautobotModelSerializer):
    """Serializer for API."""

    class Meta:
        """Meta class for ParsedNotificationSerializer."""

        model = ParsedNotification
        fields = "__all__"


class RawNotificationSerializer(NautobotModelSerializer):
    """Serializer for API."""

    class Meta:
        """Meta class for RawNotificationSerializer."""

        model = RawNotification
        fields = "__all__"


class NoteSerializer(NautobotModelSerializer):
    """Serializer for API."""

    class Meta:
        """Meta class for MaintenanceNoteSerializer."""

        model = Note
        fields = "__all__"


class NotificationSourceSerializer(NautobotModelSerializer):
    """Serializer for NotificationSource records."""

    class Meta:
        """Meta class for NotificationSourceSerializer."""

        model = NotificationSource
        fields = "__all__"


class CircuitImpactSerializer(NautobotModelSerializer):
    """Serializer for API."""

    class Meta:
        """Meta class for CircuitImpactSerializer."""

        model = CircuitImpact
        fields = "__all__"
