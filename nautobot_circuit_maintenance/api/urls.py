"""Django API urlpatterns declaration for nautobot_circuit_maintenance app."""

from nautobot.apps.api import OrderedDefaultRouter

from nautobot_circuit_maintenance.api import views

router = OrderedDefaultRouter()
# add the name of your api endpoint, usually hyphenated model name in plural, e.g. "my-model-classes"
router.register("maintenance", views.MaintenanceTaskView)
router.register("note", views.MaintenanceNoteTaskView)
router.register("circuitimpact", views.MaintenanceCircuitImpactTaskView)
router.register("notificationsource", views.NotificationSourceTaskView)
router.register("parsednotification", views.ParsedNotificationTaskView)
router.register("rawnotification", views.RawNotificationTaskView)

app_name = "nautobot_circuit_maintenance-api"
urlpatterns = router.urls
