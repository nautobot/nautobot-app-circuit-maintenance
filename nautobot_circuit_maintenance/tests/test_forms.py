"""Test circuitmaintenance forms."""

from django.test import TestCase

from nautobot_circuit_maintenance import forms


class CircuitMaintenanceTest(TestCase):
    """Test CircuitMaintenance forms."""

    def test_specifying_all_fields_success(self):
        form = forms.CircuitMaintenanceForm(
            data={
                "name": "Development",
                "description": "Development Testing",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_specifying_only_required_success(self):
        form = forms.CircuitMaintenanceForm(
            data={
                "name": "Development",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_validate_name_circuitmaintenance_is_required(self):
        form = forms.CircuitMaintenanceForm(data={"description": "Development Testing"})
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors["name"])
