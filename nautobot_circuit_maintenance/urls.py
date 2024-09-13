"""URLS for Circuit Maintenance."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.extras.views import ObjectChangeLogView

from . import views
from .models import CircuitImpact, CircuitMaintenance, Note, NotificationSource

urlpatterns = [
    # Overview
    path("maintenances/overview/", views.CircuitMaintenanceOverview.as_view(), name="circuitmaintenance_overview"),
    #  Maintenance
    path("maintenances/", views.CircuitMaintenanceListView.as_view(), name="circuitmaintenance_list"),
    path("maintenances/add/", views.CircuitMaintenanceEditView.as_view(), name="circuitmaintenance_add"),
    path("maintenances/import/", views.CircuitMaintenanceBulkImportView.as_view(), name="circuitmaintenance_import"),
    path("maintenances/edit/", views.CircuitMaintenanceBulkEditView.as_view(), name="circuitmaintenance_bulk_edit"),
    path(
        "maintenances/delete/", views.CircuitMaintenanceBulkDeleteView.as_view(), name="circuitmaintenance_bulk_delete"
    ),
    path("maintenances/<uuid:pk>/", views.CircuitMaintenanceView.as_view(), name="circuitmaintenance"),
    path("maintenances/<uuid:pk>/edit/", views.CircuitMaintenanceEditView.as_view(), name="circuitmaintenance_edit"),
    path(
        "maintenances/<uuid:pk>/delete/", views.CircuitMaintenanceDeleteView.as_view(), name="circuitmaintenance_delete"
    ),
    path(
        "maintenances/<uuid:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="circuitmaintenance_changelog",
        kwargs={"model": CircuitMaintenance},
    ),
    path("maintenances/job/", views.CircuitMaintenanceJobView.as_view(), name="circuitmaintenance_job"),
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
    # Notes
    path("notes/", views.NoteListView.as_view(), name="note_list"),
    path("notes/add/", views.NoteEditView.as_view(), name="note_add"),
    path("notes/<uuid:pk>/edit/", views.NoteEditView.as_view(), name="note_edit"),
    path("notes/<uuid:pk>/delete/", views.NoteDeleteView.as_view(), name="note_delete"),
    path("notes/<uuid:pk>/", views.NoteView.as_view(), name="note"),
    path("notes/edit/", views.NoteBulkEditView.as_view(), name="note_bulk_edit"),
    path("notes/delete/", views.NoteBulkDeleteView.as_view(), name="note_bulk_delete"),
    path("notes/import/", views.NoteBulkImportView.as_view(), name="note_import"),
    path("notes/<uuid:pk>/changelog/", ObjectChangeLogView.as_view(), name="note_changelog", kwargs={"model": Note}),
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
    path("docs/", RedirectView.as_view(url=static("nautobot_circuit_maintenances/docs/index.html")), name="docs"),
]
