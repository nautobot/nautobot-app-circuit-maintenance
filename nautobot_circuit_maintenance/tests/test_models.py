"""Unit tests for nautobot_circuit_maintenance models."""
import datetime

from django.test import TestCase
from nautobot.circuits.models import Circuit
from nautobot.circuits.models import CircuitType
from nautobot.circuits.models import Provider
from nautobot.extras.models import Status

from nautobot_circuit_maintenance.choices import CircuitImpactChoices
from nautobot_circuit_maintenance.models import CircuitImpact
from nautobot_circuit_maintenance.models import CircuitMaintenance
from nautobot_circuit_maintenance.models import NotificationSource
from nautobot_circuit_maintenance.models import RawNotification


class CircuitMaintenanceModelTestCase(TestCase):
    """Test the Circuit Maintenance models."""

    def setUp(self):
        """Setup objects for Circuit Maintenance Model tests."""
        providers = Provider.objects.bulk_create(
            (
                Provider(name="Provider 3"),
                Provider(name="Provider 4"),
            )
        )

        circuit_types = CircuitType.objects.bulk_create(
            (
                CircuitType(name="Circuit Type 3"),
                CircuitType(name="Circuit Type 4"),
            )
        )

        status = Status.objects.get(name="Active")

        circuits = Circuit.objects.bulk_create(
            (
                Circuit(cid="Circuit 4", provider=providers[0], circuit_type=circuit_types[0], status=status),
                Circuit(cid="Circuit 5", provider=providers[1], circuit_type=circuit_types[1], status=status),
                Circuit(cid="Circuit 6", provider=providers[1], circuit_type=circuit_types[0], status=status),
            )
        )

        maintenances = CircuitMaintenance.objects.bulk_create(
            (
                CircuitMaintenance(
                    name="UT-TEST-3", start_time="2020-10-04 10:00:00Z", end_time="2020-10-04 12:00:00Z"
                ),
                CircuitMaintenance(
                    name="UT-TEST-4", start_time="2020-10-05 10:00:00Z", end_time="2020-10-05 12:00:00Z"
                ),
            )
        )

        CircuitImpact.objects.bulk_create(
            (
                CircuitImpact(maintenance=maintenances[0], circuit=circuits[0]),
                CircuitImpact(maintenance=maintenances[1], circuit=circuits[0]),
            )
        )

    def test_default_impact(self):
        """Verify default impact is default to OUTAGE."""
        circuit_impacts = CircuitImpact.objects.all()
        for circuit_impact in circuit_impacts:
            self.assertEqual(circuit_impact.impact, CircuitImpactChoices.OUTAGE)


class RawNotificationModelTestCase(TestCase):
    """Test the RawNotification model."""

    def setUp(self):
        """Setup objects for Circuit Maintenance Model tests."""
        self.provider = Provider.objects.create(name="Provider 1")
        self.source = NotificationSource.objects.create(name="Source 1")

    def test_future_stamp_validation(self):
        """Validate that a stamp reference in the future raises a ValidationError."""
        stamp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
        raw_notification = RawNotification(
            raw=b"",
            subject="something",
            provider=self.provider,
            source=self.source,
            stamp=stamp,
        )
        with self.assertLogs(logger="nautobot_circuit_maintenance.models", level="WARNING") as log_res:
            raw_notification.full_clean()
            self.assertIn(
                f"WARNING:nautobot_circuit_maintenance.models:Stamp time {stamp} is not consistent, it's in the future.",
                log_res.output,
            )
