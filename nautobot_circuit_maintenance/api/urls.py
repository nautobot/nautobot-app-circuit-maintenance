"""Django API urlpatterns declaration for nautobot_circuit_maintenance app."""

from nautobot.apps.api import OrderedDefaultRouter

from nautobot_circuit_maintenance.api import views

router = OrderedDefaultRouter()
# add the name of your api endpoint, usually hyphenated model name in plural, e.g. "my-model-classes"
router.register("circuitmaintenance", views.CircuitMaintenanceViewSet)

urlpatterns = router.urls
