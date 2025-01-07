"""Django urlpatterns declaration for nautobot_circuit_maintenance app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter


from nautobot_circuit_maintenance import views


router = NautobotUIViewSetRouter()

router.register("circuitmaintenance", views.CircuitMaintenanceUIViewSet)


urlpatterns = [
    path("docs/", RedirectView.as_view(url=static("nautobot_circuit_maintenance/docs/index.html")), name="docs"),
]

urlpatterns += router.urls
