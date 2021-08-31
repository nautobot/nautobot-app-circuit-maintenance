"""Test cases for application metrics endpoint views."""
from datetime import datetime, timedelta
from django.test import TestCase
from nautobot.circuits.models import Circuit, CircuitType, Provider, CircuitTermination
from nautobot.dcim.models import Site

from nautobot_circuit_maintenance.metrics_app import metric_circuit_operational
from nautobot_circuit_maintenance.models import CircuitMaintenance, CircuitImpact


class AppMetricTests(TestCase):
    """Test cases for ensuring application metric endpoint is working properly."""

    def setUp(self):
        """Setup objects to run the test."""
        for test_id in range(5):
            # Creating 5 Providers
            setattr(
                self,
                f"provider_{test_id}",
                Provider.objects.create(name=f"Provider {test_id}", slug=f"provider-{test_id}"),
            )
            # Creating 5 CircuitTypes
            setattr(
                self,
                f"circuit_type_{test_id}",
                CircuitType.objects.create(name=f"Circuit Type {test_id}", slug=f"circuit-type-{test_id}"),
            )
            # Createing 5 Circuits
            setattr(
                self,
                f"circuit_{test_id}",
                Circuit.objects.create(
                    cid=f"Circuit {test_id}",
                    provider=getattr(self, f"provider_{test_id}"),
                    type=getattr(self, f"circuit_type_{test_id}"),
                ),
            )

            if test_id < 4:
                # Creating 4 Sites
                setattr(
                    self,
                    f"site_{test_id}",
                    Site.objects.create(name=f"Site {test_id}", slug=f"site-{test_id}"),
                )
                # Creating 4 CircuitTerminations
                term_side = "A" if (test_id % 2) == 0 else "Z"
                CircuitTermination.objects.create(
                    circuit=getattr(self, f"circuit_{test_id}"),
                    term_side=term_side,
                    site=getattr(self, f"site_{test_id}"),
                )

        self.circuit_maintenance_1 = CircuitMaintenance.objects.create(
            name="Circuit Maintenance 1",
            status="CONFIRMED",
            start_time=datetime.utcnow() - timedelta(minutes=1),
            end_time=datetime.utcnow() + timedelta(minutes=1),
        )
        self.circuit_maintenance_3 = CircuitMaintenance.objects.create(
            name="Circuit Maintenance 3",
            status="CONFIRMED",
            start_time=datetime.utcnow() + timedelta(minutes=20),
            end_time=datetime.utcnow() + timedelta(minutes=21),
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
                self.assertEqual(sample.labels["site"], getattr(self, f"site_{test_id}").name)
                if test_id == "1":
                    self.assertEqual(sample.value, 2)
                else:
                    self.assertEqual(sample.value, 1)
