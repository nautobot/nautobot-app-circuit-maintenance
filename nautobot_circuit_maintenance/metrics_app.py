"""Nautobot Circuit Maintenance plugin application level metrics exposed through nautobot_capacity_metrics."""
from collections import OrderedDict
import functools
from datetime import datetime
from prometheus_client.core import CounterMetricFamily
from nautobot.circuits.models import Circuit
from django.conf import settings

from .models import CircuitImpact, CircuitMaintenance


def rgetattr(obj, attr, *args):
    """Recursive GetAttr to look for nested attributes."""

    def _getattr(obj, attr):
        """Extract the nested value. If the value supports `all()` we return the first valid object."""
        value = getattr(obj, attr, *args)

        try:
            for item in value.all():
                try:
                    return item
                except AttributeError:
                    pass
        except AttributeError:
            pass

        return value

    return functools.reduce(_getattr, [obj] + attr.split("."))


PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("nautobot_circuit_maintenance", {})
DEFAULT_LABELS = OrderedDict(
    {
        "circuit": "cid",
        "provider": "provider.name",
        "circuit_type": "type.name",
        "site": "terminations.site.name",
    }
)


def metric_circuit_operational():
    """Expose the operational state of CircuitImpacts when a Maintenance is ongoing.

    # Circuit operational
    circuit_maintenance_status{"circuit": "XXXXX", provider="ntt", circuit_type="peering", site='XX"} 1.0

    # Circuit in maintenance mode
    circuit_maintenance_status{"circuit": "YYYYYY", provider="ntt", circuit_type="peering", site='YY"} 2.0
    """
    labels = PLUGIN_SETTINGS.get("metrics", {}).get("labels_attached", OrderedDict(DEFAULT_LABELS))

    counters = CounterMetricFamily(
        "nautobot_circuit_maintenance",
        "Circuit operational status",
        labels=list(labels.keys()),
    )

    # Statuses that we understand a Circuit Maintenance is expected to run
    # Not all the providers use all the standard statuses.
    active_statuses = ["CONFIRMED", "IN-PROCESS", "RE-SCHEDULED"]
    active_circuit_maintenances = CircuitMaintenance.objects.filter(
        status__in=active_statuses, start_time__lte=datetime.utcnow(), end_time__gte=datetime.utcnow()
    )

    active_circuit_impacts = CircuitImpact.objects.filter(maintenance__in=active_circuit_maintenances).exclude(
        impact="NO-IMPACT"
    )

    for circuit in Circuit.objects.all().prefetch_related("circuitimpact_set"):
        status = 1
        if any(circuit_impact in active_circuit_impacts for circuit_impact in circuit.circuitimpact_set.all()):
            status = 2

        values = []
        for _, attr in labels.items():
            try:
                label_value = rgetattr(circuit, attr)
            except AttributeError:
                label_value = "n/a"
            values.append(label_value)

        counters.add_metric(
            values,
            status,
        )

    yield counters
