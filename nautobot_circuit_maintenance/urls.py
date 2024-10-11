"""URLS for Circuit Maintenance."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.core.views.routers import NautobotUIViewSetRouter
from nautobot.extras.views import ObjectChangeLogView

from . import views
from .models import CircuitImpact, NotificationSource

router = NautobotUIViewSetRouter()
router.register("maintenance", views.CircuitMaintenanceUIViewSet)

urlpatterns = [
    # Overview
    path("circuit-maintenances/overview/", views.CircuitMaintenanceOverview.as_view(), name="circuitmaintenance_overview"),
    path("circuit-maintenances/job/", views.CircuitMaintenanceJobView.as_view(), name="circuitmaintenance_job"),
    # Circuit Impact
    path("circuit-impacts/", views.CircuitImpactListView.as_view(), name="circuitimpact_list"),
    path("circuit-impacts/add/", views.CircuitImpactEditView.as_view(), name="circuitimpact_add"),
    path("circuit-impacts/<uuid:pk>/", views.CircuitImpactView.as_view(), name="circuitimpact"),
    path(
        "circuit-impacts/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="circuitimpact_changelog",
        kwargs={"model": CircuitImpact},
    ),
    path("circuit-impacts/<uuid:pk>/edit/", views.CircuitImpactEditView.as_view(), name="circuitimpact_edit"),
    path("circuit-impacts/<uuid:pk>/delete/", views.CircuitImpactDeleteView.as_view(), name="circuitimpact_delete"),
    path("circuit-impacts/edit/", views.CircuitImpactBulkEditView.as_view(), name="circuitimpact_bulk_edit"),
    path("circuit-impacts/delete/", views.CircuitImpactBulkDeleteView.as_view(), name="circuitimpact_bulk_delete"),
    path("circuit-impacts/import/", views.CircuitImpactBulkImportView.as_view(), name="circuitimpact_import"),
    # Raw Notification
    path("raw-notifications/", views.RawNotificationListView.as_view(), name="rawnotification_list"),
    path("raw-notifications/<uuid:pk>/", views.RawNotificationView.as_view(), name="rawnotification"),
    path("raw-notifications/<uuid:pk>/delete/", views.RawNotificationDeleteView.as_view(), name="rawnotification_delete"),
    path(
        "raw-notifications/delete/",
        views.RawNotificationBulkDeleteView.as_view(),
        name="rawnotification_bulk_delete",
    ),
    # Parsed Notification
    path(
        "parsed-notifications/<uuid:pk>/",
        views.ParsedNotificationView.as_view(),
        name="parsednotification",
    ),
    # Notification Source
    path("notification-sources/", views.NotificationSourceListView.as_view(), name="notificationsource_list"),
    path("notification-sources/google_authorize/<str:name>/", views.google_authorize, name="google_authorize"),
    path("notification-sources/google_oauth2callback/", views.google_oauth2callback, name="google_oauth2callback"),
    path("notification-sources/edit/", views.NotificationSourceBulkEditView.as_view(), name="notificationsource_bulk_edit"),
    path("notification-sources/<uuid:pk>/edit/", views.NotificationSourceEditView.as_view(), name="notificationsource_edit"),
    path("notification-sources/<uuid:pk>/", views.NotificationSourceView.as_view(), name="notificationsource"),
    path("notification-sources/<uuid:pk>/validate/", views.NotificationSourceValidate.as_view(), name="notificationsource_validate"),
    path(
        "notification-sources/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="notificationsource_changelog",
        kwargs={"model": NotificationSource},
    ),
    path("docs/", RedirectView.as_view(url=static("nautobot_circuit_maintenance/docs/index.html")), name="docs"),
]

urlpatterns += router.urls
