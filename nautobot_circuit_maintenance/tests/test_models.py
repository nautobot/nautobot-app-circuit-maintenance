"""Test CircuitMaintenance."""

from nautobot.apps.testing import ModelTestCases

from nautobot_circuit_maintenance import models
from nautobot_circuit_maintenance.tests import fixtures


class TestCircuitMaintenance(ModelTestCases.BaseModelTestCase):
    """Test CircuitMaintenance."""

    model = models.CircuitMaintenance

    @classmethod
    def setUpTestData(cls):
        """Create test data for CircuitMaintenance Model."""
        super().setUpTestData()
        # Create 3 objects for the model test cases.
        fixtures.create_circuitmaintenance()

    def test_create_circuitmaintenance_only_required(self):
        """Create with only required fields, and validate null description and __str__."""
        circuitmaintenance = models.CircuitMaintenance.objects.create(name="Development")
        self.assertEqual(circuitmaintenance.name, "Development")
        self.assertEqual(circuitmaintenance.description, "")
        self.assertEqual(str(circuitmaintenance), "Development")

    def test_create_circuitmaintenance_all_fields_success(self):
        """Create CircuitMaintenance with all fields."""
        circuitmaintenance = models.CircuitMaintenance.objects.create(name="Development", description="Development Test")
        self.assertEqual(circuitmaintenance.name, "Development")
        self.assertEqual(circuitmaintenance.description, "Development Test")
