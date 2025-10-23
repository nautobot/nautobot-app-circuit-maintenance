"""Views for nautobot_circuit_maintenance."""

from nautobot.apps.views import NautobotUIViewSet
from nautobot.apps.ui import ObjectDetailContent, ObjectFieldsPanel, ObjectsTablePanel, SectionChoices
from nautobot.core.templatetags import helpers

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

    # Here is an example of using the UI  Component Framework for the detail view.
    # More information can be found in the Nautobot documentation:
    # https://docs.nautobot.com/projects/core/en/stable/development/core/ui-component-framework/
    object_detail_content = ObjectDetailContent(
        panels=[
            ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields="__all__",
                # Alternatively, you can specify a list of field names:
                # fields=[
                #     "name",
                #     "description",
                # ],
                # Some fields may require additional configuration, we can use value_transforms
                # value_transforms={
                #     "name": [helpers.bettertitle]
                # },
            ),
            # If there is a ForeignKey or M2M with this model we can use ObjectsTablePanel
            # to display them in a table format.
            # ObjectsTablePanel(
                # weight=200,
                # section=SectionChoices.RIGHT_HALF,
                # table_class=tables.CircuitMaintenanceTable,
                # You will want to filter the table using the related_name
                # filter="circuitmaintenances",
            # ),
        ],
    )
