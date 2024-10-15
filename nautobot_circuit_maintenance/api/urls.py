"""URLS for Circuit Maintenance API."""

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register("circuit-maintenances", views.MaintenanceTaskView)
router.register("circuit-impacts", views.MaintenanceCircuitImpactTaskView)
router.register("notification-sources", views.NotificationSourceTaskView)
router.register("parsed-notifications", views.ParsedNotificationTaskView)
router.register("raw-notifications", views.RawNotificationTaskView)

app_name = "nautobot_circuit_maintenance-api"  # pylint: disable=invalid-name
urlpatterns = router.urls
