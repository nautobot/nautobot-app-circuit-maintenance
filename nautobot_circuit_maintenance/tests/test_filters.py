"""Test CircuitMaintenance Filter."""

from nautobot.apps.testing import FilterTestCases

from nautobot_circuit_maintenance import filters, models
from nautobot_circuit_maintenance.tests import fixtures


class CircuitMaintenanceFilterTestCase(FilterTestCases.FilterTestCase):
    """CircuitMaintenance Filter Test Case."""

    queryset = models.CircuitMaintenance.objects.all()
    filterset = filters.CircuitMaintenanceFilterSet
    generic_filter_tests = (
        ("id",),
        ("created",),
        ("last_updated",),
        ("name",),
    )

    @classmethod
    def setUpTestData(cls):
        """Setup test data for CircuitMaintenance Model."""
        fixtures.create_circuitmaintenance()

    def test_q_search_name(self):
        """Test using Q search with name of CircuitMaintenance."""
        params = {"q": "Test One"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_invalid(self):
        """Test using invalid Q search for CircuitMaintenance."""
        params = {"q": "test-five"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
