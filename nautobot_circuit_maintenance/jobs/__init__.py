"""Circuit Maintenance plugin jobs."""

# pylint: disable=no-name-in-module
from nautobot_circuit_maintenance.handle_notifications.handler import HandleCircuitMaintenanceNotifications
from nautobot_circuit_maintenance.jobs.site_search import FindSitesWithMaintenanceOverlap


jobs = [FindSitesWithMaintenanceOverlap, HandleCircuitMaintenanceNotifications]
