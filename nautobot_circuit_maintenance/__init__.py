"""App declaration for nautobot_circuit_maintenance."""
# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
from importlib import metadata

from nautobot.apps import NautobotAppConfig

__version__ = metadata.version(__name__)


class NautobotCircuitMaintenanceConfig(NautobotAppConfig):
    """App configuration for the nautobot_circuit_maintenance app."""

    name = "nautobot_circuit_maintenance"
    verbose_name = "Circuit Maintenance Management"
    version = __version__
    author = "Network to Code, LLC"
    description = "Nautobot app to automatically handle Circuit Maintenances Notifications."
    base_url = "circuit-maintenance"
    min_version = "2.0.0"
    max_version = "2.99"
    required_settings = []
    default_settings = {
        "raw_notification_initial_days_since": 7,
        "raw_notification_size": 8192,
        "dashboard_n_days": 30,
        "overlap_job_exclude_no_impact": False,
    }
    caching_config = {}
    home_view_name = "plugins:nautobot_circuit_maintenance:circuitmaintenance_overview"

    def ready(self):
        super().ready()
        post_migrate.connect(custom_fields_extension, sender=self)
        post_migrate.connect(import_notification_sources, sender=self)

        # App metrics are disabled by default
        if settings.PLUGINS_CONFIG.get("nautobot_circuit_maintenance", {}).get("metrics", {}).get("enable", False):
            # pylint: disable=import-outside-toplevel
            from nautobot_capacity_metrics import register_metric_func
            from .metrics_app import metric_circuit_operational

            register_metric_func(metric_circuit_operational)


config = CircuitMaintenanceConfig  # pylint:disable=invalid-name
