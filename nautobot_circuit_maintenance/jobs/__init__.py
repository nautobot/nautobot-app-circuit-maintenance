"""Circuit Maintenance jobs."""
from .handle_notifications import HandleCircuitMaintenanceNotifications

jobs = (HandleCircuitMaintenanceNotifications,)

__all__ = ("jobs",)
