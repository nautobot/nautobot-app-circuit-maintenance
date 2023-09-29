"""Circuit Maintenance plugin jobs."""
from nautobot.core.celery import register_jobs

from nautobot_circuit_maintenance.handle_notifications.handler import HandleCircuitMaintenanceNotifications
from nautobot_circuit_maintenance.jobs.location_search import FindLocationsWithMaintenanceOverlap


jobs = [FindLocationsWithMaintenanceOverlap, HandleCircuitMaintenanceNotifications]

register_jobs(*jobs)
