"""Circuit Maintenance plugin jobs."""
from .handle_notifications.handler import HandleCircuitMaintenanceNotifications


jobs = [HandleCircuitMaintenanceNotifications]
