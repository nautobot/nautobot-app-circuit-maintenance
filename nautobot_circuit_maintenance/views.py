"""Views for nautobot_circuit_maintenance."""

from nautobot.apps.views import NautobotUIViewSet

from nautobot_circuit_maintenance import filters, forms, models, tables
from nautobot_circuit_maintenance.api import serializers


class CircuitMaintenanceUIViewSet(NautobotUIViewSet):
    """ViewSet for CircuitMaintenance views."""

    bulk_update_form_class = forms.CircuitMaintenanceBulkEditForm
    filterset_class = filters.CircuitMaintenanceFilterSet
    filterset_form_class = forms.CircuitMaintenanceFilterForm
    form_class = forms.CircuitMaintenanceForm
    lookup_field = "pk"
    queryset = models.CircuitMaintenance.objects.all()
    serializer_class = serializers.CircuitMaintenanceSerializer
    table_class = tables.CircuitMaintenanceTable
