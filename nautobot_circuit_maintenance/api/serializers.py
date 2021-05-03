"""Serializer for Circuit Maintenance API."""
from rest_framework import serializers
from nautobot.circuits.api.serializers import CircuitSerializer
from nautobot_circuit_maintenance.models import CircuitImpact, CircuitMaintenance, Note


class CircuitMaintenanceCircuitImpactSerializer(serializers.ModelSerializer):
    """Serializer for API."""

    circuit = CircuitSerializer

    class Meta:
        """Meta class for MaintenanceCircuitImpactSerializer."""

        model = CircuitImpact
        fields = ["id", "maintenance", "circuit", "impact"]


class CircuitMaintenanceSerializer(serializers.ModelSerializer):
    """Serializer for API."""

    circuits = CircuitMaintenanceCircuitImpactSerializer

    class Meta:
        """Meta class for MaintenanceSerializer."""

        model = CircuitMaintenance
        fields = ["id", "name", "start_time", "end_time", "description", "status", "ack"]


class NoteSerializer(serializers.ModelSerializer):
    """Serializer for API."""

    maintenance = CircuitMaintenanceSerializer

    class Meta:
        """Meta class for MaintenanceNoteSerializer."""

        model = Note
        fields = ["id", "maintenance", "title", "comment"]
