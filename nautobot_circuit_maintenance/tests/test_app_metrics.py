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
        self.provider = Provider.objects.create(name="Provider 1", slug="provider-1")
        self.circuit_type = CircuitType.objects.create(name="Circuit Type 1", slug="circuit-type-1")
        self.circuit = Circuit.objects.create(cid="Circuit 1", provider=self.provider, type=self.circuit_type)
        self.circuit_2 = Circuit.objects.create(cid="Circuit 2", provider=self.provider, type=self.circuit_type)
        self.circuit_3 = Circuit.objects.create(cid="Circuit 3", provider=self.provider, type=self.circuit_type)
        self.site = Site.objects.create(name="Site 1", slug="site-1")
        CircuitTermination.objects.create(circuit=self.circuit, term_side="A", site=self.site)
        self.circuit_maintenance = CircuitMaintenance.objects.create(
            name="Circuit Maintenance 1",
            status="CONFIRMED",
            start_time=datetime.utcnow() - timedelta(minutes=1),
            end_time=datetime.utcnow() + timedelta(minutes=1),
        )
        CircuitImpact.objects.create(circuit=self.circuit, maintenance=self.circuit_maintenance)
        CircuitImpact.objects.create(circuit=self.circuit_3, maintenance=self.circuit_maintenance, impact="NO-IMPACT")

    def test_metric_circuit_operational(self):
        """Ensure the metric_circuit_operational command is working properly."""
        circuit_metrics = metric_circuit_operational()
        for circuit_metric in circuit_metrics:
            self.assertIsInstance(circuit_metric.name, str)
            self.assertIsInstance(circuit_metric.samples, list)
            self.assertEqual(len(circuit_metric.samples), 3)
            for sample in circuit_metric.samples:
                self.assertEqual(sample.labels["provider"], self.provider.name)
                self.assertEqual(sample.labels["circuit_type"], self.circuit_type.name)
                if sample.labels["circuit"] == self.circuit.cid:
                    self.assertEqual(sample.labels["site"], self.site.name)
                    self.assertEqual(sample.value, 2)
                else:
                    self.assertEqual(sample.labels["site"], "n/a")
                    self.assertEqual(sample.value, 1)
