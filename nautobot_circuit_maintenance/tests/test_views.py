"""Unit tests for views."""

from nautobot.apps.testing import ViewTestCases

from nautobot_circuit_maintenance import models
from nautobot_circuit_maintenance.tests import fixtures


class CircuitMaintenanceViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    # pylint: disable=too-many-ancestors
    """Test the CircuitMaintenance views."""

    model = models.CircuitMaintenance
    bulk_edit_data = {"description": "Bulk edit views"}
    form_data = {
        "name": "Test 1",
        "description": "Initial model",
    }

    update_data = {
        "name": "Test 2",
        "description": "Updated model",
    }

    @classmethod
    def setUpTestData(cls):
        fixtures.create_circuitmaintenance()
