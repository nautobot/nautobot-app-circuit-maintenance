"""Test CircuitMaintenance."""

from django.test import TestCase

from nautobot_circuit_maintenance import models


class TestCircuitMaintenance(TestCase):
    """Test CircuitMaintenance."""

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
