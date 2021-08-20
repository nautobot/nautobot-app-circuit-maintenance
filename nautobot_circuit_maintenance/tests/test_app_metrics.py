"""Test cases for application metrics endpoint views."""
from datetime import datetime, timedelta
from django.test import TestCase
from nautobot.circuits.models import Circuit, CircuitType, Provider, CircuitTermination
from nautobot.dcim.models import Site

from nautobot_circuit_maintenance.metrics_app import metric_active_maintenances
from nautobot_circuit_maintenance.models import CircuitMaintenance, CircuitImpact


class AppMetricTests(TestCase):
    """Test cases for ensuring application metric endpoint is working properly."""

    def setUp(self):
        """Setup objects to run the test."""
        self.provider = Provider.objects.create(name="Provider 1M", slug="provider-1m")
        self.circuit_type = CircuitType.objects.create(name="Circuit Type 1M", slug="circuit-type-1m")
        self.circuit = Circuit.objects.create(cid="Circuit 1M", provider=self.provider, type=self.circuit_type)
        self.site = Site.objects.create(name="Site 1M", slug="site-1m")
        self.circuit_termination = CircuitTermination.objects.create(
            circuit=self.circuit, term_side="A", site=self.site
        )
        self.circuit_maintenace = CircuitMaintenance.objects.create(
            name="Circuit Maintenance 1M",
            status="CONFIRMED",
            start_time=datetime.utcnow() - timedelta(minutes=1),
            end_time=datetime.utcnow() + timedelta(minutes=1),
        )
        self.circuit_impact = CircuitImpact.objects.create(circuit=self.circuit, maintenance=self.circuit_maintenace)

    def test_metric_active_maintenances(self):
        """Ensure the metric_active_maintenances command is working properly."""
        circuit_impacts = metric_active_maintenances()
        for circuit_impact in circuit_impacts:
            self.assertIsInstance(circuit_impact.name, str)
            self.assertIsInstance(circuit_impact.samples, list)
            self.assertEqual(len(circuit_impact.samples), 1)
            self.assertEqual(circuit_impact.samples[0].labels["circuit_maintenance"], self.circuit_maintenace.name)
            self.assertEqual(circuit_impact.samples[0].labels["circuit"], self.circuit.cid)
            self.assertEqual(circuit_impact.samples[0].labels["impact"], self.circuit_impact.impact)
            self.assertEqual(circuit_impact.samples[0].labels["provider"], self.provider.name)
            self.assertEqual(circuit_impact.samples[0].labels["circuit_type"], self.circuit_type.name)
            self.assertEqual(circuit_impact.samples[0].labels["site"], self.site.name)

    def tearDown(self) -> None:
        # TODO: remove
        pass
