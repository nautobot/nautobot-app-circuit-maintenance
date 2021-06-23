"""Notifications jobs."""
import datetime
import traceback
from typing import Union
from django.conf import settings
from django.db import OperationalError
from circuit_maintenance_parser import ParsingError, init_provider
from nautobot.circuits.models import Circuit, Provider
from nautobot.extras.jobs import Job
from nautobot_circuit_maintenance.models import (
    CircuitImpact,
    CircuitMaintenance,
    Note,
    ParsedNotification,
    RawNotification,
    NotificationSource,
)
from .sources import get_notifications, MaintenanceNotification


# pylint: disable=broad-except
PLUGIN_SETTINGS = settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]


def create_circuit_maintenance(
    logger: Job, maintenance_id: str, parsed_notification: ParsedNotification
) -> CircuitMaintenance:
    """Handles the creation of a new circuit maintenance."""
    provider = Provider.objects.filter(slug=parsed_notification.slug()).last()

    circuit_maintenance_entry = CircuitMaintenance.objects.create(
        name=maintenance_id,
        start_time=datetime.datetime.fromtimestamp(parsed_notification.start),
        end_time=datetime.datetime.fromtimestamp(parsed_notification.end),
        description=parsed_notification.summary,
        status=parsed_notification.status,
    )
    logger.log_success(obj=circuit_maintenance_entry, message="Created Circuit Maintenance.")

    for circuit in parsed_notification.circuits:
        circuit_entry = Circuit.objects.filter(cid=circuit.circuit_id, provider=provider.pk).last()
        if circuit_entry:
            circuit_impact_entry = CircuitImpact.objects.create(
                maintenance=circuit_maintenance_entry,
                circuit=circuit_entry,
                impact=circuit.impact,
            )
            logger.log_success(
                circuit_impact_entry,
                message=f"Circuit ID {circuit.circuit_id} linked to Maintenance {maintenance_id}",
            )
        else:
            note_entry = Note.objects.create(
                maintenance=circuit_maintenance_entry,
                title=f"Nonexistent circuit ID {circuit.circuit_id}",
                comment=(
                    f"Circuit ID {circuit.circuit_id} referenced was not found in the database, so omitted from the "
                    "maintenance."
                ),
                level="WARNING",
            )
            logger.log_warning(
                note_entry,
                message=(
                    f"Circuit ID {circuit.circuit_id} referenced in {maintenance_id} is not in the Database, adding a "
                    "note"
                ),
            )
    if not CircuitImpact.objects.filter(maintenance=circuit_maintenance_entry):
        logger.log_warning(message=f"Circuit Maintenance {maintenance_id} has no valid Circuit IDs")

    return circuit_maintenance_entry


def update_circuit_maintenance(
    logger: Job,
    circuit_maintenance_entry: CircuitMaintenance,
    maintenance_id: str,
    parsed_notification: ParsedNotification,
):  # pylint: disable=too-many-locals
    """Handles the update of an existent circuit maintenance."""
    provider = Provider.objects.filter(slug=parsed_notification.slug()).last()

    circuit_maintenance_entry.description = parsed_notification.summary
    circuit_maintenance_entry.status = parsed_notification.status
    circuit_maintenance_entry.start_time = datetime.datetime.fromtimestamp(parsed_notification.start)
    circuit_maintenance_entry.end_time = datetime.datetime.fromtimestamp(parsed_notification.end)
    circuit_maintenance_entry.ack = False
    circuit_maintenance_entry.save()

    circuit_entries = CircuitImpact.objects.filter(maintenance=circuit_maintenance_entry)

    parsed_cids = {parsed_circuit.circuit_id for parsed_circuit in parsed_notification.circuits}
    existing_cids = {circuit_entry.circuit.cid for circuit_entry in circuit_entries}

    cids_to_update = parsed_cids & existing_cids
    cids_to_create = parsed_cids - existing_cids
    cids_to_remove = existing_cids - parsed_cids

    for cid in cids_to_create:
        circuit_entry = Circuit.objects.filter(cid=cid, provider=provider.pk).last()
        circuit = [
            parsed_circuit for parsed_circuit in parsed_notification.circuits if parsed_circuit.circuit_id == cid
        ][0]
        if circuit_entry:
            circuit_impact_entry = CircuitImpact.objects.create(
                maintenance=circuit_maintenance_entry,
                circuit=circuit_entry,
                impact=circuit.impact,
            )
            logger.log_success(
                circuit_impact_entry,
                message=f"Circuit ID {circuit.circuit_id} linked to Maintenance {maintenance_id}",
            )
        else:
            note_entry, created = Note.objects.get_or_create(
                maintenance=circuit_maintenance_entry,
                title=f"Nonexistent circuit ID {circuit.circuit_id}",
                comment=(
                    f"Circuit ID {circuit.circuit_id} referenced was not found in the database, so omitted from the "
                    "maintenance."
                ),
                level="WARNING",
            )
            if created:
                logger.log_warning(
                    note_entry,
                    message=(
                        f"Circuit ID {circuit.circuit_id} referenced in {maintenance_id} is not in the Database, "
                        "adding a note"
                    ),
                )

    for cid in cids_to_update:
        circuit_entry = Circuit.objects.filter(cid=cid, provider=provider.pk).last()
        circuitimpact_entry = CircuitImpact.objects.filter(
            circuit=circuit_entry, maintenance=circuit_maintenance_entry
        ).last()
        circuit = [
            parsed_circuit for parsed_circuit in parsed_notification.circuits if parsed_circuit.circuit_id == cid
        ][0]
        circuitimpact_entry.impact = circuit.impact
        circuitimpact_entry.save()

    for cid in cids_to_remove:
        circuit_entry = Circuit.objects.filter(cid=cid, provider=provider.pk).last()
        CircuitImpact.objects.filter(circuit=circuit_entry, maintenance=circuit_maintenance_entry).delete()

    logger.log_info(obj=circuit_maintenance_entry, message=f"Updated Circuit Maintenance {maintenance_id}")


def process_parsed_notification(logger: Job, parsed_notification: ParsedNotification, raw_entry: RawNotification):
    """Processes a Parsed Notification, creating or updating the related Circuit Maintenance."""
    maintenance_id = str(parsed_notification.maintenance_id)
    circuit_maintenance_entry = CircuitMaintenance.objects.filter(name=maintenance_id).last()

    if circuit_maintenance_entry:
        update_circuit_maintenance(logger, circuit_maintenance_entry, maintenance_id, parsed_notification)
    else:
        circuit_maintenance_entry = create_circuit_maintenance(logger, maintenance_id, parsed_notification)

    # Insert parsed notification in DB
    parsed_entry = ParsedNotification.objects.create(
        maintenance=circuit_maintenance_entry,
        raw_notification=raw_entry,
        json=parsed_notification.to_json(),
    )
    logger.log_success(parsed_entry, message=f"Saved Parsed Notification for {maintenance_id}.")


def process_raw_notification(logger: Job, notification: MaintenanceNotification) -> Union[int, None]:
    """Processes a raw notification (maybe containing multiple parsed notifications).

    It creates a RawNotification and if it could be parsed, create the corresponding ParsedNotification.
    """
    provider = Provider.objects.filter(slug=notification.provider_type).last()

    if not provider:
        logger.log_warning(
            message=(
                f"Raw notification not created because is referencing to a provider not existent: {notification.provider_type}"
            )
        )
        return None

    for raw_payload in notification.raw_payloads:
        parser = init_provider(raw=raw_payload, provider_type=notification.provider_type)
        if not parser:
            logger.log_warning(message=f"Notification Parser not found for {notification.provider_type}")
            return None

        try:
            parsed_notifications = parser.process()
            break
        except ParsingError as exc:
            tb_str = traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__)
            logger.log_debug(message=f"Parsing failed for notification {notification.subject}:.\n{tb_str}")
        except Exception as exc:
            tb_str = traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__)
            logger.log_debug(
                message=f"Unexpected exception while parsing notification {notification.subject}.\n{tb_str}"
            )
    else:
        parsed_notifications = []
        raw_payload = b""
        logger.log_warning(message=f"Parsed failed for all the raw payloads for '{notification.subject}'.")

    if isinstance(raw_payload, str):
        raw_payload = raw_payload.encode("utf-8")

    # Insert raw notification in DB even failed parsing
    try:
        raw_entry, created = RawNotification.objects.get_or_create(
            subject=notification.subject,
            provider=provider,
            raw=raw_payload,
            sender=notification.sender,
            source=NotificationSource.objects.filter(name=notification.source).last(),
        )
    except OperationalError as exc:
        logger.log_warning(message=f"Raw notification '{notification.subject}' not created because {str(exc)}")
        return None

    if not created:
        logger.log_warning(message=f"Raw notification '{raw_entry.subject}' already existed with id {raw_entry.pk}")
        return None

    logger.log_success(raw_entry, message="Raw notification created.")

    for parsed_notification in parsed_notifications:
        try:
            process_parsed_notification(logger, parsed_notification, raw_entry)
            # Update raw notification as properly parsed
            raw_entry.parsed = True
            raw_entry.save()
        except Exception as exc:
            tb_str = traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__)
            logger.log_warning(
                parsed_notification,
                message=f"Unexpected exception while handling parsed notification {notification.subject}.\n{tb_str}",
            )

    return raw_entry.id


class HandleCircuitMaintenanceNotifications(Job):
    """Job to handle external circuit maintenance notifications and turn them into Circuit Maintenances."""

    class Meta:
        """Meta object boilerplate for HandleParsedNotifications."""

        name = "Update Circuit Maintenances"
        description = (
            "Fetch Circuit Maintenance Notifications from Source and create or update Circuit Maintenances accordingly"
        )

    def run(self, data=None, commit=None):
        """Fetch notifications, process them and update Circuit Maintenance accordingly."""
        self.log_debug("Starting Handle Notifications job.")
        raw_notification_ids = []
        notification_sources = NotificationSource.objects.all()
        if not notification_sources:
            self.log_warning(message="No notification sources configured to retrieve notifications from.")
            return raw_notification_ids

        # Latest retrieved notification will limit the scope of notifications to retrieve
        last_raw_notification = RawNotification.objects.last()
        if last_raw_notification:
            last_time_processed = last_raw_notification.date.timestamp()
            self.log_info(message=f"Processing notifications since {last_raw_notification.date}")
        else:
            last_time_processed = None

        try:
            notifications = get_notifications(
                logger=self,
                notification_sources=notification_sources,
                since=last_time_processed,
            )
            if not notifications:
                self.log_info(message="No notifications received.")
                return raw_notification_ids

            for notification in notifications:
                self.log_info(message=f"Processing notification {notification.subject}.")
                raw_id = process_raw_notification(self, notification)
                if raw_id:
                    raw_notification_ids.append(raw_id)

        except Exception as error:
            self.log_failure(message=f"Unexpected exception in Handle Notifications Job: {error}")

        self.log_debug(f"{len(raw_notification_ids)} notifications processed.")
        return raw_notification_ids
