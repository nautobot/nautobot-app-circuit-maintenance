"""URLS for Circuit Maintenance."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter

from . import views

app_name = "nautobot_circuit_maintenance"

router = NautobotUIViewSetRouter()
router.register("impact", views.CircuitImpactUIViewSet)
router.register("maintenance", views.CircuitMaintenanceUIViewSet)
router.register("note", views.NoteUIViewSet)
router.register("rawnotification", views.RawNotificationUIViewSet)
router.register("source", views.NotificationSourceUIViewSet)

urlpatterns = [
    # Overview
    path("maintenance/overview/", views.CircuitMaintenanceOverview.as_view(), name="circuitmaintenance_overview"),
    # Parsed Notification
    path(
        "parsednotification/<uuid:pk>/",
        views.ParsedNotificationView.as_view(),
        name="parsednotification",
    ),
    # Notification Source
    path("source/google_authorize/<str:name>/", views.google_authorize, name="google_authorize"),
    path("source/google_oauth2callback/", views.google_oauth2callback, name="google_oauth2callback"),
    path("docs/", RedirectView.as_view(url=static("nautobot_circuit_maintenance/docs/index.html")), name="docs"),
]

urlpatterns += router.urls
