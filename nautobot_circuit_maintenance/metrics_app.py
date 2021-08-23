"""Nautobot Circuit Maintenance plugin application level metrics exposed through nautobot_capacity_metrics."""
from datetime import datetime
from prometheus_client.core import CounterMetricFamily
from django.core.exceptions import ObjectDoesNotExist
from nautobot.circuits.models import CircuitTermination, Circuit

from .models import CircuitMaintenance, CircuitImpact


def metric_circuit_operational():
    """Expose the operational state of CircuitImpacts when a Maintenance is ongoing.

    # Circuit operational
    circuit_maintenance_status{"circuit": "XXXXX", provider="ntt", circuit_type="peering", site='XX"} 1.0

    # Circuit in maintenance mode
    circuit_maintenance_status{"circuit": "YYYYYY", provider="ntt", circuit_type="peering", site='YY"} 2.0
    """
    counters = CounterMetricFamily(
        "nautobot_circuit_maintenance",
        "Circuit operational status",
        labels=["circuit", "provider", "circuit_type", "site"],
    )

    # Statuses that we understand a Circuit Maintenance is expected to run
    # Not all the providers use all the standard statuses.
    active_statuses = ["CONFIRMED", "IN-PROCESS", "RE-SCHEDULED"]
    active_circuit_maintenances = CircuitMaintenance.objects.filter(
        status__in=active_statuses, start_time__lte=datetime.utcnow(), end_time__gte=datetime.utcnow()
    )

    for circuit in Circuit.objects.all():
        status = 1
        if CircuitImpact.objects.filter(circuit=circuit, maintenance__in=active_circuit_maintenances):
            status = 2

        try:
            circuit_termination = CircuitTermination.objects.get(circuit_id=circuit.id)
            site_name = circuit_termination.site.name
        except ObjectDoesNotExist:
            site_name = "n/a"

        counters.add_metric(
            [
                circuit.cid,
                circuit.provider.name,
                circuit.type.name,
                site_name,
            ],
            status,
        )

    yield counters
