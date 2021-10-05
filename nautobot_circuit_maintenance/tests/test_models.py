"""Unit tests for nautobot_circuit_maintenance models."""
import datetime
from django.test import TestCase

from nautobot.circuits.models import Circuit, CircuitType, Provider
from nautobot_circuit_maintenance.models import CircuitMaintenance, CircuitImpact, RawNotification, NotificationSource
from nautobot_circuit_maintenance.choices import CircuitImpactChoices


class CircuitMaintenanceModelTestCase(TestCase):
    """Test the Circuit Maintenance models."""

    def setUp(self):
        """Setup objects for Circuit Maintenance Model tests."""
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

        self.circuits = (
            Circuit(cid="Circuit 4", provider=providers[0], type=circuit_types[0]),
            Circuit(cid="Circuit 5", provider=providers[1], type=circuit_types[1]),
            Circuit(cid="Circuit 6", provider=providers[1], type=circuit_types[0]),
        )
        Circuit.objects.bulk_create(self.circuits)

        self.maintenances = [
            CircuitMaintenance(name="UT-TEST-3", start_time="2020-10-04 10:00:00", end_time="2020-10-04 12:00:00"),
            CircuitMaintenance(name="UT-TEST-4", start_time="2020-10-05 10:00:00", end_time="2020-10-05 12:00:00"),
        ]
        CircuitMaintenance.objects.bulk_create(self.maintenances)

        self.circuit_impacts = [
            CircuitImpact(
                maintenance=self.maintenances[0],
                circuit=self.circuits[0],
            ),
            CircuitImpact(
                maintenance=self.maintenances[1],
                circuit=self.circuits[0],
            ),
        ]
        CircuitImpact.objects.bulk_create(self.circuit_impacts)

    def test_default_impact(self):
        """Verify default impact is default to OUTAGE."""
        circuit_impacts = CircuitImpact.objects.all()
        for circuit_impact in circuit_impacts:
            self.assertEqual(circuit_impact.impact, CircuitImpactChoices.OUTAGE)


class RawNotificationModelTestCase(TestCase):
    """Test the RawNotification model."""

    def setUp(self):
        """Setup objects for Circuit Maintenance Model tests."""
        self.provider = Provider.objects.create(name="Provider 1", slug="provider-1")
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
