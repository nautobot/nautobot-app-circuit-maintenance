"""URLS for Circuit Maintenance API."""
from rest_framework import routers

from .views import MaintenanceNoteTaskView, MaintenanceTaskView, MaintenanceCircuitImpactTaskView

router = routers.DefaultRouter()
router.register("maintenance", MaintenanceTaskView)
router.register("note", MaintenanceNoteTaskView)
router.register("circuitimpact", MaintenanceCircuitImpactTaskView)

app_name = "nautobot_circuit_maintenance-api"  # pylint: disable=invalid-name
urlpatterns = router.urls
