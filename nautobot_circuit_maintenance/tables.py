"""Tables for Circuit Maintenance."""
import django_tables2 as tables

from nautobot.utilities.tables import BaseTable, ToggleColumn

from .models import CircuitMaintenance, RawNotification, CircuitImpact, NotificationSource, Note


class CircuitMaintenanceTable(BaseTable):
    """Table to display maintenace model."""

    name = tables.Column(linkify=True)
    circuits = tables.ManyToManyColumn(linkify_item=True)
    providers = tables.ManyToManyColumn(linkify_item=True)

    pk = ToggleColumn()

    class Meta(BaseTable.Meta):
        """Meta for class CircuitMaintenanceTable."""

        model = CircuitMaintenance
        fields = ("pk", "ack", "name", "status", "providers", "circuits", "start_time", "end_time")


class RawNotificationTable(BaseTable):
    """Table to display Raw Notifications model."""

    subject = tables.Column(linkify=True)
    source = tables.Column(linkify=True)
    provider = tables.Column(linkify=True)

    pk = ToggleColumn()

    class Meta(BaseTable.Meta):
        """Meta for class CircuitMaintenanceNofiticationRawTable."""

        model = RawNotification
        fields = ("pk", "subject", "provider", "sender", "source", "parsed", "stamp")


class CircuitImpactTable(BaseTable):
    """Table to display Circuit Impact model."""

    pk = ToggleColumn()
    maintenance = tables.Column(linkify=True)
    circuit = tables.Column(linkify=True)
    impact = tables.Column(linkify=True)

    class Meta(BaseTable.Meta):
        """Meta for class CircuitImpactTable."""

        model = CircuitImpact
        fields = ("pk", "maintenance", "circuit", "impact")


class NoteTable(BaseTable):
    """Table to display Note model."""

    pk = ToggleColumn()
    maintenance = tables.Column(linkify=True)
    title = tables.Column(linkify=True)

    class Meta(BaseTable.Meta):
        """Meta for class NoteTable."""

        model = Note
        fields = ("pk", "maintenance", "title", "level", "comment", "last_updated")


class NotificationSourceTable(BaseTable):
    """Table to display Circuit Impact model."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    providers = tables.ManyToManyColumn(linkify_item=True)

    class Meta(BaseTable.Meta):
        """Meta for class NotificationSourceTable."""

        model = NotificationSource
        fields = ("pk", "name", "slug", "attach_all_providers", "providers")
