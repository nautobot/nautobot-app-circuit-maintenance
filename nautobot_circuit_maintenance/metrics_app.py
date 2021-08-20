"""Nautobot Circuit Maintenance plugin application level metrics exposed through nautobot_capacity_metrics."""
from datetime import datetime
from prometheus_client.core import CounterMetricFamily
from django.core.exceptions import ObjectDoesNotExist
from nautobot.circuits.models import CircuitTermination

from .models import CircuitMaintenance, CircuitImpact


def metric_active_maintenances():
    """Expose the operational state of CircuitImpacts when a Maintenance is ongoing.

    # Circuit in maintenance mode
    circuit_maintenance_status{"circuit": "YYYYYY", provider="ntt", circuit_type="peering", site='YY"} 1.0
    """
    counters = CounterMetricFamily(
        "nautobot_circuit_maintenance",
        "Active Circuit Maintenances per circuit",
        labels=["circuit_maintenance", "circuit", "impact", "provider", "circuit_type", "site"],
    )

    # Statuses that we understand a Circuit Maintenance is expected to run
    # Not all the providers use all the standard statuses.
    active_statuses = ["CONFIRMED", "IN-PROCESS", "RE-SCHEDULED"]
    active_circuit_maintenances = CircuitMaintenance.objects.filter(
        status__in=active_statuses, start_time__lte=datetime.utcnow(), end_time__gte=datetime.utcnow()
    )
    if not active_circuit_maintenances:
        yield counters

    for circuit_maintenance in active_circuit_maintenances:
        impacted_circuits = CircuitImpact.objects.filter(maintenance=circuit_maintenance)
        for impacted_circuit in impacted_circuits:

            try:
                circuit_termination = CircuitTermination.objects.get(circuit_id=impacted_circuit.circuit.id)
                site_name = circuit_termination.site.name
            except ObjectDoesNotExist:
                site_name = "n/a"

            counters.add_metric(
                [
                    circuit_maintenance.name,
                    impacted_circuit.circuit.cid,
                    impacted_circuit.impact,
                    impacted_circuit.circuit.provider.name,
                    impacted_circuit.circuit.type.name,
                    site_name,
                ],
                1,
            )

    yield counters
