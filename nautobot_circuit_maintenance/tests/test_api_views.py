"""Unit tests for nautobot_circuit_maintenance."""

from nautobot.apps.testing import APIViewTestCases

from nautobot_circuit_maintenance import models
from nautobot_circuit_maintenance.tests import fixtures


class CircuitMaintenanceAPIViewTest(APIViewTestCases.APIViewTestCase):
    # pylint: disable=too-many-ancestors
    """Test the API viewsets for CircuitMaintenance."""

    model = models.CircuitMaintenance
    create_data = [
        {
            "name": "Test Model 1",
            "description": "test description",
        },
        {
            "name": "Test Model 2",
        },
    ]
    bulk_update_data = {"description": "Test Bulk Update"}

    @classmethod
    def setUpTestData(cls):
        fixtures.create_circuitmaintenance()
