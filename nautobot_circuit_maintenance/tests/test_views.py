# pylint: disable=duplicate-code,too-many-public-methods
"""Test for Circuit Maintenace Views."""
from unittest import skip
from unittest.mock import patch
from datetime import datetime, timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from nautobot.users.models import ObjectPermission

from nautobot.circuits.models import Circuit, CircuitType, Provider
from nautobot.utilities.testing import ViewTestCases, ModelViewTestCase
from nautobot_circuit_maintenance.models import (
    CircuitMaintenance,
    CircuitImpact,
    Note,
    NotificationSource,
    ParsedNotification,
    RawNotification,
)
from nautobot_circuit_maintenance.views import CircuitMaintenanceOverview


class CircuitMaintenanceTest(ViewTestCases.PrimaryObjectViewTestCase):
    """View tests for CircuitMaintenance."""

    model = CircuitMaintenance

    def _get_base_url(self):
        return f"plugins:{self.model._meta.app_label}:{self.model._meta.model_name}_{{}}"

    def assertInstanceEqual(self, instance, data, api=False):  # pylint: disable=arguments-differ
        """Used to overwrite inbuilt function. Causing type issues for datetimepicker."""

    @skip("Not implemented yet.")
    def test_has_advanced_tab(self):
        pass

    @skip("Not implemented yet.")
    def test_get_object_notes(self):
        pass

    @classmethod
    def setUpTestData(cls):
        """Setup environment for testing."""
        CircuitMaintenance.objects.create(
            name="UT-TEST-1", start_time="2020-10-04 10:00:00", end_time="2020-10-04 12:00:00"
        )
        CircuitMaintenance.objects.create(
            name="UT-TEST-2", start_time="2020-10-05 10:00:00", end_time="2020-10-05 12:00:00"
        )

        cls.form_data = {
            "name": "UT-TEST-10",
            "start_time": "2020-10-06 10:00:00",
            "end_time": "2020-10-06 12:00:00",
            "description": "TEST 0 descr",
        }

        cls.csv_data = (
            "name,start_time,end_time,description",
            "UT-TEST-20, 2020-10-06 10:00:00, 2020-10-06 12:00:00, TEST 20 descr",
            "UT-TEST-21, 2020-10-06 10:00:00, 2020-10-06 12:00:00, TEST 21 descr",
            "UT-TEST-22, 2020-10-06 10:00:00, 2020-10-06 12:00:00, TEST 22 descr",
        )

        cls.bulk_edit_data = {
            "status": "CANCELLED",
        }


class CircuitImpactTest(ViewTestCases.OrganizationalObjectViewTestCase):
    """View tests for CircuitImpact."""

    model = CircuitImpact

    def _get_base_url(self):
        return f"plugins:{self.model._meta.app_label}:{self.model._meta.model_name}_{{}}"

    def assertInstanceEqual(self, instance, data, api=False):  # pylint: disable=arguments-differ
        """Used to overwrite inbuilt function. Causing type issues for datetimepicker."""

    @skip("Not implemented yet.")
    def test_has_advanced_tab(self):
        pass

    @skip("Not implemented yet.")
    def test_get_object_notes(self):
        pass

    @skip("Not implemented yet.")
    def test_list_objects_unknown_filter_no_strict_filtering(self):
        pass

    @skip("Not implemented yet.")
    def test_list_objects_unknown_filter_strict_filtering(self):
        pass

    @classmethod
    def setUpTestData(cls):
        """Setup environment for testing."""
        providers = (
            Provider(name="Provider 3", slug="provider-3"),
            Provider(name="Provider 4", slug="provider-4"),
        )
        Provider.objects.bulk_create(providers)

        circuit_types = (
            CircuitType(name="Circuit Type 3", slug="circuit-type-3"),
            CircuitType(name="Circuit Type 4", slug="circuit-type-4"),
        )
        CircuitType.objects.bulk_create(circuit_types)

        circuits = (
            Circuit(cid="Circuit 4", provider=providers[0], type=circuit_types[0]),
            Circuit(cid="Circuit 5", provider=providers[1], type=circuit_types[1]),
            Circuit(cid="Circuit 6", provider=providers[1], type=circuit_types[0]),
            Circuit(cid="Circuit 7", provider=providers[1], type=circuit_types[0]),
            Circuit(cid="Circuit 8", provider=providers[1], type=circuit_types[0]),
        )
        Circuit.objects.bulk_create(circuits)

        existing_maintenance = [
            CircuitMaintenance(name="UT-TEST-3", start_time="2020-10-04 10:00:00", end_time="2020-10-04 12:00:00"),
            CircuitMaintenance(name="UT-TEST-4", start_time="2020-10-05 10:00:00", end_time="2020-10-05 12:00:00"),
        ]
        CircuitMaintenance.objects.bulk_create(existing_maintenance)

        circuit_impacts = [
            CircuitImpact(
                maintenance=existing_maintenance[0],
                circuit=circuits[0],
            ),
            CircuitImpact(
                maintenance=existing_maintenance[1],
                circuit=circuits[0],
            ),
        ]
        CircuitImpact.objects.bulk_create(circuit_impacts)

        cls.form_data = {"maintenance": existing_maintenance[0], "circuit": circuits[1], "impact": "NO-IMPACT"}

        cls.csv_data = (
            "maintenance,circuit,impact",
            f"{existing_maintenance[0].pk}, {circuits[2].pk}, NO-IMPACT",
            f"{existing_maintenance[0].pk}, {circuits[3].pk}, OUTAGE",
            f"{existing_maintenance[0].pk}, {circuits[4].pk}, DEGRADED",
        )

        cls.bulk_edit_data = {
            "impact": "OUTAGE",
        }

    def test_list_objects_with_constrained_permission(self):
        """TODO: fix because it's checking the get_absolute_url() in a wrong page."""


class NoteTest(ViewTestCases.OrganizationalObjectViewTestCase):
    """View tests for Note."""

    model = Note

    def _get_base_url(self):
        return f"plugins:{self.model._meta.app_label}:{self.model._meta.model_name}_{{}}"

    def assertInstanceEqual(self, instance, data, api=False):  # pylint: disable=arguments-differ
        """Used to overwrite inbuilt function. Causing type issues for datetimepicker."""

    @skip("Not implemented yet.")
    def test_has_advanced_tab(self):
        pass

    @skip("Not implemented yet.")
    def test_get_object_anonymous(self):
        pass

    @skip("Not Implemented")
    def test_list_objects_unknown_filter_no_strict_filtering(self):
        pass

    @skip("Not Implemented")
    def test_list_objects_unknown_filter_strict_filtering(self):
        pass

    @skip("Not Implemented")
    def test_get_object_notes(self):
        pass

    @classmethod
    def setUpTestData(cls):
        """Setup environment for testing."""

        maintenance = CircuitMaintenance.objects.create(
            name="UT-TEST-1", start_time="2020-10-04 10:00:00", end_time="2020-10-04 12:00:00"
        )

        Note.objects.create(maintenance=maintenance, title="Note 1", comment="comment 1")
        Note.objects.create(maintenance=maintenance, title="Note 2", comment="comment 2")

        cls.form_data = {"maintenance": maintenance, "title": "Note 3", "level": "INFO", "comment": "comment 3"}

        cls.csv_data = (
            "maintenance,title,comment",
            f"{maintenance.pk}, Note 4, comment 4",
            f"{maintenance.pk}, Note 5, comment 5",
        )

        cls.bulk_edit_data = {"level": "WARNING"}

    def test_list_objects_with_constrained_permission(self):
        """TODO: fix because it's checking the get_absolute_url() in a wrong page."""


class NotificationSourceTest(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    # ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    # ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    # ViewTestCases.BulkImportObjectsViewTestCase,
    # ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    """View tests for NotificationSource."""

    model = NotificationSource

    def _get_base_url(self):
        return f"plugins:{self.model._meta.app_label}:{self.model._meta.model_name}_{{}}"

    def assertInstanceEqual(self, instance, data, api=False):  # pylint: disable=arguments-differ
        """Used to overwrite inbuilt function. Causing type issues for datetimepicker."""

    @skip("Not implemented yet.")
    def test_has_advanced_tab(self):
        pass

    @skip("Not implemented yet.")
    def test_get_object_anonymous(self):
        pass

    @classmethod
    def setUpTestData(cls):
        """Setup environment for testing."""
        providers = (
            Provider(name="Provider 3", slug="provider-3"),
            Provider(name="Provider 4", slug="provider-4"),
        )
        Provider.objects.bulk_create(providers)

        notificationsource_1 = NotificationSource.objects.create(name="whatever 1", slug="whatever-1")
        notificationsource_2 = NotificationSource.objects.create(name="whatever 2", slug="whatever-2")

        notificationsource_1.providers.set(providers)
        notificationsource_2.providers.set(providers)

        cls.form_data = {
            "name": "whatever 3",
            "slug": "whatever-3",
            "providers": providers,
        }

        cls.csv_data = (
            "name,slug",
            "whatever 4,whatever-4",
            "whatever 5,whatever-5",
        )

        cls.SOURCE_1 = {
            "name": "example",
            "account": "me@example.com",
            "secret": "supersecret",
            "url": "imap://example.com",
        }
        settings.PLUGINS_CONFIG = {"nautobot_circuit_maintenance": {"notification_sources": [cls.SOURCE_1.copy()]}}
        NotificationSource.objects.create(name=cls.SOURCE_1["name"], slug=cls.SOURCE_1["name"])

    @patch("nautobot_circuit_maintenance.handle_notifications.sources.IMAP.test_authentication")
    def test_validate_view_ok(self, mock_test_authentication):
        """Test for custom NotificationSourceValidate view."""
        mock_test_authentication.return_value = True, "Test OK"

        # Adding test to user to run Validate
        obj_perm = ObjectPermission(name="Test permission", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        response = self.client.get(
            self._get_queryset().get(name=self.SOURCE_1["name"]).get_absolute_url() + "validate/"
        )
        self.assertContains(response, "SUCCESS: Test OK", status_code=200)

    @patch("nautobot_circuit_maintenance.handle_notifications.sources.IMAP.test_authentication")
    def test_validate_view_ko(self, mock_test_authentication):
        """Test for custom NotificationSourceValidate view."""
        mock_test_authentication.return_value = False, "Some error"

        # Adding test to user to run Validate
        obj_perm = ObjectPermission(name="Test permission", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        response = self.client.get(
            self._get_queryset().get(name=self.SOURCE_1["name"]).get_absolute_url() + "validate/"
        )
        self.assertContains(response, "FAILED: Some error", status_code=200)

    def test_list_objects_with_constrained_permission(self):
        """TODO: fix because it's checking the get_absolute_url() in a wrong page."""


class RawNotificationTest(
    ViewTestCases.GetObjectViewTestCase,
    # ViewTestCases.GetObjectChangelogViewTestCase,
    # ViewTestCases.CreateObjectViewTestCase,
    # ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    # ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    """View tests for RawNotification."""

    model = RawNotification

    def _get_base_url(self):
        return f"plugins:{self.model._meta.app_label}:{self.model._meta.model_name}_{{}}"

    def assertInstanceEqual(self, instance, data, api=False):  # pylint: disable=arguments-differ
        """Used to overwrite inbuilt function. Causing type issues for datetimepicker."""

    @classmethod
    def setUpTestData(cls):
        """Setup environment for testing."""
        providers = (
            Provider(name="Provider 3", slug="provider-3"),
            Provider(name="Provider 4", slug="provider-4"),
        )
        Provider.objects.bulk_create(providers)

        source = NotificationSource.objects.create(name="whatever 1", slug="whatever-1")

        RawNotification.objects.create(
            subject="whatever",
            provider=providers[0],
            sender="whatever",
            source=source,
            raw=b"whatever 1",
            stamp=datetime.now(timezone.utc),
        )

        RawNotification.objects.create(
            subject="whatever",
            provider=providers[1],
            source=source,
            raw=b"whatever 2",
            stamp=datetime.now(timezone.utc),
        )

    def test_list_objects_with_constrained_permission(self):
        """TODO: fix because it's checking the get_absolute_url() in a wrong page."""

    @skip("Not implemented yet.")
    def test_has_advanced_tab(self):
        pass

    @skip("Not implemented yet.")
    def test_get_object_anonymous(self):
        pass


class ParsedNotificationTest(
    ViewTestCases.GetObjectViewTestCase,
    # ViewTestCases.GetObjectChangelogViewTestCase,
    # ViewTestCases.CreateObjectViewTestCase,
    # ViewTestCases.EditObjectViewTestCase,
    # ViewTestCases.DeleteObjectViewTestCase,
    # ViewTestCases.ListObjectsViewTestCase,
    # ViewTestCases.BulkImportObjectsViewTestCase,
    # ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    """View tests for ParsedNotification."""

    model = ParsedNotification

    def _get_base_url(self):
        return f"plugins:{self.model._meta.app_label}:{self.model._meta.model_name}_{{}}"

    def assertInstanceEqual(self, instance, data, api=False):  # pylint: disable=arguments-differ
        """Used to overwrite inbuilt function. Causing type issues for datetimepicker."""

    @classmethod
    def setUpTestData(cls):
        """Setup environment for testing."""
        providers = (
            Provider(name="Provider 3", slug="provider-3"),
            Provider(name="Provider 4", slug="provider-4"),
        )
        Provider.objects.bulk_create(providers)

        source = NotificationSource.objects.create(name="whatever 1", slug="whatever-1")

        raw_notification = RawNotification.objects.create(
            subject="whatever subject 1",
            provider=providers[0],
            sender="whatever sender 1",
            source=source,
            raw=b"whatever raw 1",
            stamp=datetime.now(timezone.utc),
        )
        circuit_maintenance = CircuitMaintenance.objects.create(
            name="UT-TEST-1", start_time="2020-10-04 10:00:00", end_time="2020-10-04 12:00:00"
        )
        ParsedNotification.objects.create(maintenance=circuit_maintenance, raw_notification=raw_notification, json="{}")

        raw_notification_2 = RawNotification.objects.create(
            subject="whatever subject 2",
            provider=providers[0],
            sender="whatever sender 2",
            source=source,
            raw=b"whatever raw 2",
            stamp=datetime.now(timezone.utc),
        )
        circuit_maintenance_2 = CircuitMaintenance.objects.create(
            name="UT-TEST-2", start_time="2020-10-04 10:00:00", end_time="2020-10-04 12:00:00"
        )
        ParsedNotification.objects.create(
            maintenance=circuit_maintenance_2, raw_notification=raw_notification_2, json="{}"
        )

    @skip("Not implemented yet.")
    def test_has_advanced_tab(self):
        pass

    @skip("Not implemented yet.")
    def test_get_object_anonymous(self):
        pass


class DashboardTest(ModelViewTestCase):
    """View tests for CircuitMaintenance Dashboard."""

    model = CircuitMaintenance

    def _get_base_url(self):
        return f"plugins:{self.model._meta.app_label}:{self.model._meta.model_name}_{{}}"

    def assertInstanceEqual(self, instance, data, api=False):  # pylint: disable=arguments-differ
        """Used to overwrite inbuilt function. Causing type issues for datetimepicker."""

    @classmethod
    def setUpTestData(cls):
        """Setup environment for testing."""
        cls.maintenances_before = []
        cls.maintenances_after = []
        cls.seven_days = []
        cls.thirty_days = []
        cls.year_days = []
        cls.test_date = datetime.strptime("2022-08-25", "%Y-%m-%d").date()
        circuit_maintenances_create_list = [
            {
                "name": "UT-TEST-1",
                "start_time": "2022-08-24 10:00:00",
                "end_time": "2022-08-24 12:00:00",
                "lists": ["maintenances_before", "7_days"],
            },
            {
                "name": "UT-TEST-4",
                "start_time": "2022-08-16 10:00:00",
                "end_time": "2022-08-16 12:00:00",
                "lists": ["maintenances_before", "30_days"],
            },
            {
                "name": "UT-TEST-2",
                "start_time": "2022-08-26 10:00:00",
                "end_time": "2022-08-26 12:00:00",
                "lists": ["maintenances_after"],
            },
            {
                "name": "UT-TEST-3",
                "start_time": "2022-08-27 10:00:00",
                "end_time": "2022-08-27 12:00:00",
                "lists": ["maintenances_after"],
            },
            {
                "name": "UT-TEST-5",
                "start_time": "2022-03-27 10:00:00",
                "end_time": "2022-03-27 12:00:00",
                "lists": ["maintenances_before", "365_days"],
            },
        ]

        for circuit_maintenance in circuit_maintenances_create_list:
            ckt_mnt = CircuitMaintenance.objects.create(
                name=circuit_maintenance["name"],
                start_time=circuit_maintenance["start_time"],
                end_time=circuit_maintenance["end_time"],
            )

            # Check for each list to append the maintenance test to
            print(circuit_maintenance["lists"])
            if "maintenances_before" in circuit_maintenance["lists"]:
                cls.maintenances_before.append(ckt_mnt)

            if "maintenances_after" in circuit_maintenance["lists"]:
                cls.maintenances_after.append(ckt_mnt)

            if "7_days" in circuit_maintenance["lists"]:
                cls.seven_days.append(ckt_mnt)
                cls.thirty_days.append(ckt_mnt)
                cls.year_days.append(ckt_mnt)

            if "30_days" in circuit_maintenance["lists"]:
                cls.thirty_days.append(ckt_mnt)
                cls.year_days.append(ckt_mnt)

            if "365_days" in circuit_maintenance["lists"]:
                cls.year_days.append(ckt_mnt)

    def test_get_maintenances_next_n_days(self):
        """Test get maintenances in the next n days."""
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

        self.assertEqual(result, 2)

    def test_get_maintenances_per_month(self):
        test_object = CircuitMaintenanceOverview()
        expected_result = 5 / 6.0
        result = test_object.get_maintenances_per_month()

        self.assertEqual(expected_result, result)


class DashboardTestZeroMaintenances(ModelViewTestCase):
    """View tests for CircuitMaintenance Dashboard."""

    model = CircuitMaintenance

    def _get_base_url(self):
        return f"plugins:{self.model._meta.app_label}:{self.model._meta.model_name}_{{}}"

    def assertInstanceEqual(self, instance, data, api=False):  # pylint: disable=arguments-differ
        """Used to overwrite inbuilt function. Causing type issues for datetimepicker."""

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

    def test_get_maintenances_per_month(self):
        test_object = CircuitMaintenanceOverview()
        expected_result = 0
        result = test_object.get_maintenances_per_month()

        self.assertEqual(expected_result, result)
