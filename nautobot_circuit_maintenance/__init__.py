"""Plugin declaration for nautobot_circuit_maintenance."""
# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from importlib import metadata

__version__ = metadata.version(__name__)

from nautobot.extras.plugins import NautobotAppConfig


class NautobotCircuitMaintenanceConfig(NautobotAppConfig):
    """Plugin configuration for the nautobot_circuit_maintenance plugin."""

    name = "nautobot_circuit_maintenance"
    verbose_name = "Circuit Maintenance"
    version = __version__
    author = "Network to Code, LLC"
    description = "Nautobot plugin to automatically handle Circuit Maintenances Notifications."
    base_url = "circuit-maintenance"
    required_settings = []
    min_version = "2.0.0"
    max_version = "2.9999"
    default_settings = {}
    caching_config = {}


config = NautobotCircuitMaintenanceConfig  # pylint:disable=invalid-name
