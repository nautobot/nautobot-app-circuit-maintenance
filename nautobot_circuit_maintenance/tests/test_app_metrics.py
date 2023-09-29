"""Test cases for application metrics endpoint views."""
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from django.test import TestCase
from nautobot.circuits.models import Circuit
from nautobot.circuits.models import CircuitTermination
from nautobot.circuits.models import CircuitType
from nautobot.circuits.models import Provider
from nautobot.dcim.models import Location
from nautobot.dcim.models import LocationType
from nautobot.extras.models import Status

from nautobot_circuit_maintenance.metrics_app import metric_circuit_operational
from nautobot_circuit_maintenance.models import CircuitImpact
from nautobot_circuit_maintenance.models import CircuitMaintenance


class AppMetricTests(TestCase):
    """Test cases for ensuring application metric endpoint is working properly."""

    def setUp(self):
        """Setup objects to run the test."""
        for test_id in range(5):
            # Creating 5 Providers
            setattr(
                self,
                f"provider_{test_id}",
                Provider.objects.create(name=f"Provider {test_id}"),
            )
            # Creating 5 CircuitTypes
            setattr(
                self,
                f"circuit_type_{test_id}",
                CircuitType.objects.create(name=f"Circuit Type {test_id}"),
            )
            # Createing 5 Circuits
            setattr(
                self,
                f"circuit_{test_id}",
                Circuit.objects.create(
                    cid=f"Circuit {test_id}",
                    provider=getattr(self, f"provider_{test_id}"),
                    circuit_type=getattr(self, f"circuit_type_{test_id}"),
                    status=Status.objects.get(name="Active"),
                ),
            )

            if test_id < 4:
                location_type = LocationType.objects.get_or_create(name="Location Type")[0]
                # Creating 4 Locations
                setattr(
                    self,
                    f"location_{test_id}",
                    Location.objects.create(
                        name=f"Location {test_id}",
                        location_type=location_type,
                        status=Status.objects.get(name="Active"),
                    ),
                )
                # Creating 4 CircuitTerminations
                term_side = "A" if (test_id % 2) == 0 else "Z"
                CircuitTermination.objects.create(
                    circuit=getattr(self, f"circuit_{test_id}"),
                    term_side=term_side,
                    location=getattr(self, f"location_{test_id}"),
                )

        self.circuit_maintenance_1 = CircuitMaintenance.objects.create(
            name="Circuit Maintenance 1",
            status="CONFIRMED",
            start_time=datetime.now(timezone.utc) - timedelta(minutes=1),
            end_time=datetime.now(timezone.utc) + timedelta(minutes=1),
        )
        self.circuit_maintenance_3 = CircuitMaintenance.objects.create(
            name="Circuit Maintenance 3",
            status="CONFIRMED",
            start_time=datetime.now(timezone.utc) + timedelta(minutes=20),
            end_time=datetime.now(timezone.utc) + timedelta(minutes=21),
        )

        CircuitImpact.objects.create(circuit=getattr(self, "circuit_1"), maintenance=self.circuit_maintenance_1)
        CircuitImpact.objects.create(
            circuit=getattr(self, "circuit_2"), maintenance=self.circuit_maintenance_1, impact="NO-IMPACT"
        )
        CircuitImpact.objects.create(circuit=getattr(self, "circuit_3"), maintenance=self.circuit_maintenance_3)
        # Circuit 4 and 5 have no maintenance attached

    def test_metric_circuit_operational(self):
        """Ensure the metric_circuit_operational command is working properly."""
        circuit_metrics = metric_circuit_operational()
        for circuit_metric in circuit_metrics:
            self.assertIsInstance(circuit_metric.name, str)
            self.assertIsInstance(circuit_metric.samples, list)
            # Circuit 5 has not Termination, so it should not appear in the metrics
            self.assertEqual(len(circuit_metric.samples), 4)
            for sample in circuit_metric.samples:
                test_id = sample.labels["circuit"].split(" ")[-1]
                self.assertEqual(sample.labels["provider"], getattr(self, f"provider_{test_id}").name)
                self.assertEqual(sample.labels["circuit_type"], getattr(self, f"circuit_type_{test_id}").name)
                self.assertEqual(sample.labels["location"], getattr(self, f"location_{test_id}").name)
                if test_id == "1":
                    self.assertEqual(sample.value, 2)
                else:
                    self.assertEqual(sample.value, 1)
