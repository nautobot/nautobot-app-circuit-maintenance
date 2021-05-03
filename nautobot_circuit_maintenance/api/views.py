"""Views for API."""
from nautobot.extras.api.views import ModelViewSet
from nautobot_circuit_maintenance.models import CircuitMaintenance, Note, CircuitImpact

from .serializers import (
    NoteSerializer,
    CircuitMaintenanceSerializer,
    CircuitMaintenanceCircuitImpactSerializer,
)


class MaintenanceTaskView(ModelViewSet):
    """API view for Circuit Maintenance CRUD operations."""

    queryset = CircuitMaintenance.objects.prefetch_related()
    serializer_class = CircuitMaintenanceSerializer


class MaintenanceNoteTaskView(ModelViewSet):
    """API view for Circuit Note CRUD operations."""

    queryset = Note.objects.prefetch_related()
    serializer_class = NoteSerializer


class MaintenanceCircuitImpactTaskView(ModelViewSet):
    """API view for Circuit Impact CRUD operations."""

    queryset = CircuitImpact.objects.prefetch_related()
    serializer_class = CircuitMaintenanceCircuitImpactSerializer
