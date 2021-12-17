"""Views for API."""
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets

from nautobot.extras.api.views import CustomFieldModelViewSet
from nautobot_circuit_maintenance.models import CircuitImpact, CircuitMaintenance, Note, NotificationSource
from nautobot_circuit_maintenance import filters

from .serializers import (
    NoteSerializer,
    NotificationSourceSerializer,
    CircuitMaintenanceSerializer,
    CircuitMaintenanceCircuitImpactSerializer,
)


class MaintenanceTaskView(CustomFieldModelViewSet):
    """API view for Circuit Maintenance CRUD operations."""

    queryset = CircuitMaintenance.objects.prefetch_related()
    serializer_class = CircuitMaintenanceSerializer
    filterset_class = filters.CircuitMaintenanceFilterSet


class MaintenanceNoteTaskView(CustomFieldModelViewSet):
    """API view for Circuit Note CRUD operations."""

    queryset = Note.objects.prefetch_related()
    serializer_class = NoteSerializer


class MaintenanceCircuitImpactTaskView(CustomFieldModelViewSet):
    """API view for Circuit Impact CRUD operations."""

    queryset = CircuitImpact.objects.prefetch_related()
    serializer_class = CircuitMaintenanceCircuitImpactSerializer
    filterset_class = filters.CircuitImpactFilterSet


class NotificationSourceTaskView(viewsets.ReadOnlyModelViewSet):
    """API view for Notification Source CRUD operations."""

    queryset = NotificationSource.objects.prefetch_related()
    serializer_class = NotificationSourceSerializer
    filterset_class = filters.NotificationSourceFilterSet

    def get_serializer_context(self):
        """Add custom fields to the serializer context, as in nautobot.extras.api.views.CustomFieldModelViewSet."""
        # Gather all custom fields for the model
        content_type = ContentType.objects.get_for_model(self.queryset.model)
        custom_fields = content_type.custom_fields.all()

        context = super().get_serializer_context()
        context.update(
            {
                "custom_fields": custom_fields,
            }
        )
        return context
