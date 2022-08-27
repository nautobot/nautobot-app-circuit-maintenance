# pylint: disable=duplicate-code
"""Test for Circuit Maintenace Views."""
from unittest import skip
from unittest.mock import patch
from datetime import datetime, timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from nautobot.users.models import ObjectPermission

from nautobot.circuits.models import Circuit, CircuitType, Provider
from nautobot.utilities.testing import ViewTestCases
from nautobot_circuit_maintenance.models import (
    CircuitMaintenance,
    CircuitImpact,
    Note,
    NotificationSource,
    ParsedNotification,
    RawNotification,
)
from nautobot_circuit_maintenance.views import CircuitMaintenanceOverview


class DashboardTestZeroMaintenances(ViewTestCases.PrimaryObjectViewTestCase):
    """View tests for CircuitMaintenance Dashboard."""

    model = CircuitMaintenance

    def _get_base_url(self):
        return f"plugins:{self.model._meta.app_label}:{self.model._meta.model_name}_{{}}"

    def assertInstanceEqual(self, instance, data, api=False):  # pylint: disable=arguments-differ
        """Used to overwrite inbuilt function. Causing type issues for datetimepicker."""

    @skip("Not implemented yet.")
    def test_has_advanced_tab(self):
        pass

    @skip("Not Implemented.")
    def test_edit_object_with_permission(self):
        pass

    @skip("Not Implemented.")
    def test_edit_object_with_constrained_permission(self):
        pass

    @skip("Not Implemented.")
    def test_create_object_with_permission(self):
        pass

    @skip("Not implemented.")
    def test_create_object_with_constrained_permission(self):
        pass

    @skip("Not Implemented.")
    def test_bulk_import_objects_with_permission(self):
        pass

    @skip("Not Implemented.")
    def test_bulk_import_objects_with_constrained_permission(self):
        pass

    @skip("Not Implemented.")
    def test_bulk_edit_objects_with_constrained_permission(self):
        pass

    @skip("Not implemented.")
    def test_get_object_notes(self):
        pass

    @skip("Not implemented.")
    def test_delete_object_with_constrained_permission(self):
        pass

    @skip("Not implemented.")
    def test_delete_object_with_permission(self):
        pass

    @skip("Not implemented.")
    def test_delete_object_without_permission(self):
        pass

    @skip("Not implemented.")
    def test_edit_object_without_permission(self):
        pass

    @skip("Not implemented.")
    def test_get_object_anonymous(self):
        pass

    @skip("Not implemented.")
    def test_get_object_changelog(self):
        pass

    @skip("Not implemented.")
    def test_get_object_with_constrained_permission(self):
        pass

    @skip("Not implemented.")
    def test_get_object_with_permission(self):
        pass

    @skip("Not implemented.")
    def test_get_object_without_permission(self):
        pass

    @skip("Not implemented.")
    def test_list_objects_filtered(self):
        pass

    @skip("Not implemented.")
    def test_list_objects_unknown_filter_no_strict_filtering(self):
        pass

    @skip("Not implemented.")
    def test_list_objects_unknown_filter_strict_filtering(self):
        pass

    @skip("Not implemented.")
    def test_list_objects_with_constrained_permission(self):
        pass

    @classmethod
    def setUpTestData(cls):
        """Setup environment for testing."""
        cls.maintenances_before = []
        cls.maintenances_after = []
        cls.seven_days = []
        cls.thirty_days = []
        cls.year_days = []
        cls.test_date = datetime.strptime("2022-08-25", "%Y-%m-%d").date()

    def test_get_maintenances_next_n_days(self):
        """Test get maintenances in the next n days."""
        CircuitMaintenance.objects.all().delete()
        test_object = CircuitMaintenanceOverview()

        self.assertListEqual(
            test_object.get_maintenances_next_n_days(start_date=self.test_date, n_days=7), self.maintenances_after
        )

    def test_get_maintenance_past_n_days(self):
        """Test get maintenances in the past n days."""
        test_object = CircuitMaintenanceOverview()

        self.assertListEqual(
            test_object.get_maintenance_past_n_days(start_date=self.test_date, n_days=-7), self.seven_days
        )

    def test_get_historical_matrix(self):
        """Test of _get_historical_matrix."""
        test_object = CircuitMaintenanceOverview()
        result = test_object._get_historical_matrix(start_date=self.test_date)  # pylint: disable=protected-access

        # Testing the length of the list items, the queryset will have these in a different order.
        self.assertEqual(len(result["past_7_days_maintenance"]), len(self.seven_days))
        self.assertEqual(len(result["past_30_days_maintenance"]), len(self.thirty_days))
        self.assertEqual(len(result["past_365_days_maintenance"]), len(self.year_days))

    def test_calculate_future_maintenances(self):
        test_object = CircuitMaintenanceOverview()
        result = test_object.calculate_future_maintenances(start_date=self.test_date)

        self.assertEqual(result, 0)

    def test_get_month_list(self):
        test_object = CircuitMaintenanceOverview()
        months = test_object.get_month_list()
        expected_months = []

        self.assertListEqual(months, expected_months)

    def test_get_maintenances_per_month(self):
        test_object = CircuitMaintenanceOverview()
        expected_result = 0
        result = test_object.get_maintenances_per_month()

        self.assertEqual(expected_result, result)
