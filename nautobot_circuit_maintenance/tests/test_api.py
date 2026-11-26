"""Unit tests for nautobot_circuit_maintenance."""

from datetime import datetime, timedelta, timezone

from django.urls import reverse
from nautobot.circuits.models import Circuit, CircuitType, Provider
from nautobot.core.testing import APITestCase, APIViewTestCases
from nautobot.extras.models import Status

from nautobot_circuit_maintenance.choices import NoteLevelChoices
from nautobot_circuit_maintenance.models import CircuitImpact, CircuitMaintenance, Note


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
                "start_time": datetime.now(timezone.utc) + timedelta(days=5),
                "end_time": datetime.now(timezone.utc) + timedelta(days=6),
                "description": "TEST1",
            }
        ]

    def get_deletable_object(self):
        """Return an object that can be deleted via the API."""
        return CircuitMaintenance.objects.get_or_create(
            name="DELETABLE",
            start_time=datetime.now(timezone.utc) + timedelta(days=5),
            end_time=datetime.now(timezone.utc) + timedelta(days=6),
        )[0]


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
            Provider(name="Provider 1"),
            Provider(name="Provider 2"),
        )
        Provider.objects.bulk_create(providers)

        circuit_types = (
            CircuitType(name="Circuit Type 1"),
            CircuitType(name="Circuit Type 2"),
        )
        CircuitType.objects.bulk_create(circuit_types)

        active_status = Status.objects.get(name="Active")
        circuits = (
            Circuit(cid="Circuit 1", status=active_status, provider=providers[0], circuit_type=circuit_types[0]),
            Circuit(cid="Circuit 2", status=active_status, provider=providers[1], circuit_type=circuit_types[1]),
            Circuit(cid="Circuit 3", status=active_status, provider=providers[1], circuit_type=circuit_types[0]),
        )
        Circuit.objects.bulk_create(circuits)

        maintenances = (
            CircuitMaintenance(
                name="UT-TEST1",
                start_time=datetime.now(timezone.utc) + timedelta(days=5),
                end_time=datetime.now(timezone.utc) + timedelta(days=6),
                description="TEST1",
            ),
            CircuitMaintenance(
                name="UT-TEST2",
                start_time=datetime.now(timezone.utc) + timedelta(days=5),
                end_time=datetime.now(timezone.utc) + timedelta(days=6),
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

    def get_deletable_object(self):
        """Return an object that can be deleted via the API."""
        return CircuitImpact.objects.get_or_create(
            impact="NO-IMPACT",
            maintenance=CircuitMaintenance.objects.first(),
            circuit=Circuit.objects.first(),
        )[0]


class NoteAPIFilterTest(APITestCase):
    """The Note REST API applies `NoteFilterSet` query parameters."""

    model = Note

    @classmethod
    def setUpTestData(cls):
        maintenance = CircuitMaintenance.objects.create(
            name="UT-NOTE-API", start_time="2020-10-04 10:00:00Z", end_time="2020-10-04 12:00:00Z"
        )
        Note.objects.create(maintenance=maintenance, title="Info", level=NoteLevelChoices.INFO, comment="info")
        cls.warning = Note.objects.create(
            maintenance=maintenance, title="Warning", level=NoteLevelChoices.WARNING, comment="warning"
        )

    def test_list_filtered_by_level(self):
        self.add_permissions("nautobot_circuit_maintenance.view_note")
        url = reverse("plugins-api:nautobot_circuit_maintenance-api:note-list")
        response = self.client.get(f"{url}?level={NoteLevelChoices.WARNING}", **self.header)
        self.assertHttpStatus(response, 200)
        self.assertEqual([result["id"] for result in response.data["results"]], [str(self.warning.pk)])
