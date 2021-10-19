"""Nautobot Circuit Maintenance plugin application level metrics exposed through nautobot_capacity_metrics."""
from collections import OrderedDict
import functools
from datetime import datetime, timezone
from prometheus_client.core import GaugeMetricFamily
from nautobot.circuits.models import CircuitTermination
from django.conf import settings

from .models import CircuitImpact, CircuitMaintenance


def rgetattr(obj, attr, *args):
    """Recursive GetAttr to look for nested attributes."""

    def _getattr(obj, attr):
        """Extract the nested value. If the value supports `all()` we return the first valid object."""
        value = getattr(obj, attr, *args)

        return value

    return functools.reduce(_getattr, [obj] + attr.split("."))


PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("nautobot_circuit_maintenance", {})
# REMINDER
# If we update the list of default labels, we should also update
# the list of select_related fields for the query in metric_circuit_operational
DEFAULT_LABELS = {
    "circuit": "circuit.cid",
    "provider": "circuit.provider.name",
    "circuit_type": "circuit.type.name",
    "site": "site.name",
}


def metric_circuit_operational():
    """Expose the operational state of Circuits with a CircuitTermination when a Maintenance is ongoing.

    # Circuit operational
    circuit_maintenance_status{"circuit": "XXXXX", provider="ntt", circuit_type="peering", site='XX"} 1.0

    # Circuit in maintenance mode
    circuit_maintenance_status{"circuit": "YYYYYY", provider="ntt", circuit_type="peering", site='YY"} 2.0
    """
    labels = OrderedDict(PLUGIN_SETTINGS.get("metrics", {}).get("labels_attached", DEFAULT_LABELS))

    gauges = GaugeMetricFamily(
        "circuit_maintenance_status",
        "Circuit Maintenance status",
        labels=list(labels.keys()),
    )

    # Statuses that we understand a Circuit Maintenance is expected to run
    # Not all the providers use all the standard statuses.
    active_statuses = ["CONFIRMED", "IN-PROCESS", "RE-SCHEDULED"]
    active_circuit_maintenances = CircuitMaintenance.objects.filter(
        status__in=active_statuses, start_time__lte=datetime.now(timezone.utc), end_time__gte=datetime.now(timezone.utc)
    )

    active_circuit_impacts = (
        CircuitImpact.objects.filter(maintenance__in=active_circuit_maintenances)
        .exclude(impact="NO-IMPACT")
        .prefetch_related("circuit")
    )

    for termination in CircuitTermination.objects.all().select_related(
        "circuit", "circuit__provider", "circuit__type", "site"
    ):
        status = 1
        if any(circuit_impact.circuit == termination.circuit for circuit_impact in active_circuit_impacts):
            status = 2

        values = []
        for _, attr in labels.items():
            try:
                label_value = rgetattr(termination, attr)
                values.append(label_value)
            except AttributeError:
                pass

        gauges.add_metric(
            values,
            status,
        )

    yield gauges
