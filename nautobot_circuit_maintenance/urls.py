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
    path("maintenance/overview/", views.CircuitMaintenanceOverview.as_view(), name="circuitmaintenance_overview"),
    #  Maintenance Job
    path("maintenance/job/", views.CircuitMaintenanceJobView.as_view(), name="circuitmaintenance_job"),
    # Circuit Impact
    path("impact/", views.CircuitImpactListView.as_view(), name="circuitimpact_list"),
    path("impact/add/", views.CircuitImpactEditView.as_view(), name="circuitimpact_add"),
    path("impact/<uuid:pk>/", views.CircuitImpactView.as_view(), name="circuitimpact"),
    path(
        "impact/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="circuitimpact_changelog",
        kwargs={"model": CircuitImpact},
    ),
    path("impact/<uuid:pk>/edit/", views.CircuitImpactEditView.as_view(), name="circuitimpact_edit"),
    path("impact/<uuid:pk>/delete/", views.CircuitImpactDeleteView.as_view(), name="circuitimpact_delete"),
    path("impact/edit/", views.CircuitImpactBulkEditView.as_view(), name="circuitimpact_bulk_edit"),
    path("impact/delete/", views.CircuitImpactBulkDeleteView.as_view(), name="circuitimpact_bulk_delete"),
    path("impact/import/", views.CircuitImpactBulkImportView.as_view(), name="circuitimpact_import"),
   # Raw Notification
    path("rawnotification/", views.RawNotificationListView.as_view(), name="rawnotification_list"),
    path("rawnotification/<uuid:pk>/", views.RawNotificationView.as_view(), name="rawnotification"),
    path("rawnotification/<uuid:pk>/delete/", views.RawNotificationDeleteView.as_view(), name="rawnotification_delete"),
    path(
        "rawnotification/delete/",
        views.RawNotificationBulkDeleteView.as_view(),
        name="rawnotification_bulk_delete",
    ),
    # Parsed Notification
    path(
        "parsednotification/<uuid:pk>/",
        views.ParsedNotificationView.as_view(),
        name="parsednotification",
    ),
    # Notification Source
    path("source/", views.NotificationSourceListView.as_view(), name="notificationsource_list"),
    path("source/google_authorize/<str:name>/", views.google_authorize, name="google_authorize"),
    path("source/google_oauth2callback/", views.google_oauth2callback, name="google_oauth2callback"),
    path("source/edit/", views.NotificationSourceBulkEditView.as_view(), name="notificationsource_bulk_edit"),
    path("source/<uuid:pk>/edit/", views.NotificationSourceEditView.as_view(), name="notificationsource_edit"),
    path("source/<uuid:pk>/", views.NotificationSourceView.as_view(), name="notificationsource"),
    path("source/<uuid:pk>/validate/", views.NotificationSourceValidate.as_view(), name="notificationsource_validate"),
    path(
        "source/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="notificationsource_changelog",
        kwargs={"model": NotificationSource},
    ),
    path("docs/", RedirectView.as_view(url=static("nautobot_circuit_maintenance/docs/index.html")), name="docs"),
]

urlpatterns += router.urls
