"""Circuit Maintenance plugin jobs."""
# from nautobot.extras.models import Job

from nautobot_circuit_maintenance.handle_notifications.handler import HandleCircuitMaintenanceNotifications
from nautobot_circuit_maintenance.jobs.site_search import FindSitesWithCircuitImpact


jobs = [FindSitesWithCircuitImpact, HandleCircuitMaintenanceNotifications]
