"""Tables for Circuit Maintenance."""

import django_tables2 as tables
from nautobot.core.tables import BaseTable, ToggleColumn

from .models import CircuitImpact, CircuitMaintenance, Note, NotificationSource, ParsedNotification, RawNotification

CIRCUIT_TERMINATION_PARENT = """
{% load helpers %}
{% if value.provider_network %}
{{ value.provider_network|hyperlinked_object }}
{% elif value.location %}
{{ value.location|hyperlinked_object }}
{% elif value.cloud_network %}
{{ value.cloud_network|hyperlinked_object }}
{% else %}
{{ None|placeholder }}
{% endif %}
"""


class CircuitMaintenanceTable(BaseTable):
    """Table to display maintenace model."""

    name = tables.Column(linkify=True)
    circuits = tables.ManyToManyColumn(linkify_item=True)
    providers = tables.ManyToManyColumn(linkify_item=True)

    pk = ToggleColumn()

    class Meta(BaseTable.Meta):
        """Meta for class CircuitMaintenanceTable."""

        model = CircuitMaintenance
        fields = (  # pylint:disable=nb-use-fields-all
            "pk",
            "ack",
            "name",
            "status",
            "providers",
            "circuits",
            "start_time",
            "end_time",
        )


class RawNotificationTable(BaseTable):
    """Table to display Raw Notifications model."""

    subject = tables.Column(linkify=True)
    source = tables.Column(linkify=True)
    provider = tables.Column(linkify=True)

    pk = ToggleColumn()

    class Meta(BaseTable.Meta):
        """Meta for class CircuitMaintenanceNofiticationRawTable."""

        model = RawNotification
        fields = (  # pylint:disable=nb-use-fields-all
            "pk",
            "subject",
            "provider",
            "sender",
            "source",
            "parsed",
            "stamp",
        )


class CircuitImpactTable(BaseTable):
    """Table to display Circuit Impact model."""

    pk = ToggleColumn()
    maintenance = tables.Column(linkify=True)
    impact = tables.Column(linkify=True)

    cid = tables.Column(
        accessor="circuit__cid", verbose_name="ID", linkify=lambda record: record.circuit.get_absolute_url()
    )
    provider = tables.Column(accessor="circuit__provider", verbose_name="Provider", linkify=True)
    circuit_type = tables.Column(accessor="circuit__circuit_type", verbose_name="Type", linkify=True)
    status = tables.Column(accessor="circuit__status", verbose_name="Status")
    circuit_termination_a = tables.TemplateColumn(
        template_code=CIRCUIT_TERMINATION_PARENT,
        accessor="circuit__circuit_termination_a",
        orderable=False,
        verbose_name="A Side",
    )
    circuit_termination_z = tables.TemplateColumn(
        template_code=CIRCUIT_TERMINATION_PARENT,
        accessor="circuit__circuit_termination_z",
        orderable=False,
        verbose_name="Z Side",
    )
    description = tables.Column(accessor="circuit__description", verbose_name="Description")

    class Meta(BaseTable.Meta):
        """Table to display CircuitImpact model."""

        model = CircuitImpact
        fields = (  # pylint:disable=nb-use-fields-all
            "pk",
            "maintenance",
            "cid",
            "impact",
            "provider",
            "circuit_type",
            "status",
            "circuit_termination_a",
            "circuit_termination_z",
            "description",
        )
        default_columns = fields


class NoteTable(BaseTable):
    """Table to display Note model."""

    pk = ToggleColumn()
    maintenance = tables.Column(linkify=True)
    title = tables.Column(linkify=True)

    class Meta(BaseTable.Meta):
        """Meta for class NoteTable."""

        model = Note
        fields = (
            "pk",
            "maintenance",
            "level",
            "title",
            "last_updated",
            "comment",
        )
        default_columns = (
            "pk",
            "level",
            "title",
            "last_updated",
            "comment",
        )


class NotificationSourceTable(BaseTable):
    """Table to display NotificationSource model."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    providers = tables.ManyToManyColumn(linkify_item=True)

    class Meta(BaseTable.Meta):
        """Meta for class NotificationSourceTable."""

        model = NotificationSource
        fields = ("pk", "name", "attach_all_providers", "providers")  # pylint:disable=nb-use-fields-all


class ParsedNotificationTable(BaseTable):
    """Table to display ParsedNotification model."""

    pk = ToggleColumn()
    raw_notification_subject = tables.Column(
        accessor="raw_notification__subject", verbose_name="Raw Subject", linkify=True
    )
    raw_notification_provider = tables.Column(accessor="raw_notification__provider", verbose_name="Provider")
    stamp = tables.Column(accessor="raw_notification__stamp", verbose_name="Received")
    json = tables.Column()

    class Meta(BaseTable.Meta):
        """Meta for class ParsedNotificationTable."""

        model = ParsedNotification
        fields = (
            "pk",
            "raw_notification_subject",
            "raw_notification_provider",
            "stamp",
            "json",
        )
        default_columns = fields
