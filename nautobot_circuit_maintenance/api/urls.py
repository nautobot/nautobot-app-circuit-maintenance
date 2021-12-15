"""URLS for Circuit Maintenance API."""
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register("maintenance", views.MaintenanceTaskView)
router.register("note", views.MaintenanceNoteTaskView)
router.register("circuitimpact", views.MaintenanceCircuitImpactTaskView)
router.register("notificationsource", views.NotificationSourceTaskView)

app_name = "nautobot_circuit_maintenance-api"  # pylint: disable=invalid-name
urlpatterns = router.urls
