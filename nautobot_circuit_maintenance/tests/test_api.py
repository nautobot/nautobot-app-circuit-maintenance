"""Test for Circuit Maintenace API."""
import datetime
from django.urls import reverse
from django.utils.timezone import now
from nautobot.circuits.models import Circuit, CircuitType, Provider
from nautobot.utilities.testing import APIViewTestCases
from nautobot_circuit_maintenance.models import CircuitMaintenance, CircuitImpact


class CircuitMaintenanceTest(APIViewTestCases.CreateObjectViewTestCase):
    """API tests."""

    view_namespace = None

    def _get_view_namespace(self):
        return f"plugins-api:{self.view_namespace or self.model._meta.app_label}-api"

    def _get_detail_url(self, instance):
        viewname = f"{self._get_view_namespace()}:{instance._meta.model_name}-detail"
        return reverse(viewname, kwargs={"pk": instance.pk})

    def _get_list_url(self):
        viewname = f"{self._get_view_namespace()}:{self.model._meta.model_name}-list"
        return reverse(viewname)

    model = CircuitMaintenance
    brief_fields = ["id", "name", "start_time", "end_time", "description"]

    @classmethod
    def setUpTestData(cls):
        """Setup enviornment for testing."""
        cls.create_data = [
            {
                "name": "UT-TEST1",
                "start_time": now() + datetime.timedelta(days=5),
                "end_time": now() + datetime.timedelta(days=6),
                "description": "TEST1",
            }
        ]


class CircuitImpactTest(APIViewTestCases.CreateObjectViewTestCase):
    """API tests for Circuit Impact."""

    view_namespace = None

    def _get_view_namespace(self):
        return f"plugins-api:{self.view_namespace or self.model._meta.app_label}-api"

    model = CircuitImpact
    brief_fields = ["id", "impact", "maintenance", "circuit"]

    @classmethod
    def setUpTestData(cls):
        """Setup enviornment for testing."""
        providers = (
            Provider(name="Provider 1", slug="provider-1"),
            Provider(name="Provider 2", slug="provider-2"),
        )
        Provider.objects.bulk_create(providers)

        circuit_types = (
            CircuitType(name="Circuit Type 1", slug="circuit-type-1"),
            CircuitType(name="Circuit Type 2", slug="circuit-type-2"),
        )
        CircuitType.objects.bulk_create(circuit_types)

        circuits = (
            Circuit(cid="Circuit 1", provider=providers[0], type=circuit_types[0]),
            Circuit(cid="Circuit 2", provider=providers[1], type=circuit_types[1]),
            Circuit(cid="Circuit 3", provider=providers[1], type=circuit_types[0]),
        )
        Circuit.objects.bulk_create(circuits)

        maintenances = (
            CircuitMaintenance(
                name="UT-TEST1",
                start_time=now() + datetime.timedelta(days=5),
                end_time=now() + datetime.timedelta(days=6),
                description="TEST1",
            ),
            CircuitMaintenance(
                name="UT-TEST2",
                start_time=now() + datetime.timedelta(days=5),
                end_time=now() + datetime.timedelta(days=6),
                description="TEST2",
            ),
        )
        CircuitMaintenance.objects.bulk_create(maintenances)

        cls.create_data = [
            {
                "maintenance": maintenances[0].id,
                "circuit": circuits[0].id,
                "impact": "NO-IMPACT",
            },
            {"maintenance": maintenances[1].id, "circuit": circuits[1].id},
        ]
