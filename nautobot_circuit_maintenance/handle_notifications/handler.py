"""Notifications jobs."""
import datetime
import traceback
from typing import Optional, List
import uuid
from dateutil import parser
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from circuit_maintenance_parser import ProviderError, init_provider, NotificationData, Maintenance
from nautobot.circuits.models import Circuit, Provider
from nautobot.extras.jobs import Job, BooleanVar

from nautobot_circuit_maintenance.choices import CircuitMaintenanceStatusChoices
from nautobot_circuit_maintenance.enum import MessageProcessingStatus
from nautobot_circuit_maintenance.models import (
    CircuitImpact,
    CircuitMaintenance,
    MAX_MAINTENANCE_NAME_LENGTH,
    MAX_NOTIFICATION_SENDER_LENGTH,
    MAX_NOTIFICATION_SUBJECT_LENGTH,
    MAX_NOTE_TITLE_LENGTH,
    Note,
    ParsedNotification,
    RawNotification,
    NotificationSource,
)
from .sources import get_notifications, MaintenanceNotification


name = "Circuit Maintenance"  # pylint: disable=invalid-name


# pylint: disable=broad-except
PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("nautobot_circuit_maintenance", {})


def create_circuit_maintenance(
    logger: Job,
    notification: MaintenanceNotification,
    maintenance_id: str,
    parser_maintenance: Maintenance,
    provider: Provider,
) -> CircuitMaintenance:
    """Handles the creation of a new circuit maintenance."""
    circuit_maintenance_entry = CircuitMaintenance(
        name=maintenance_id[:MAX_MAINTENANCE_NAME_LENGTH],
        start_time=datetime.datetime.fromtimestamp(parser_maintenance.start, tz=datetime.timezone.utc),
        end_time=datetime.datetime.fromtimestamp(parser_maintenance.end, tz=datetime.timezone.utc),
        description=parser_maintenance.summary,
        status=(
            parser_maintenance.status
            if parser_maintenance.status in CircuitMaintenanceStatusChoices.values()
            else CircuitMaintenanceStatusChoices.UNKNOWN
        ),
    )
    circuit_maintenance_entry.save()
    logger.log_success(obj=circuit_maintenance_entry, message="Created Circuit Maintenance.")

    for circuit in parser_maintenance.circuits:
        circuit_entry = Circuit.objects.filter(cid__iexact=circuit.circuit_id, provider=provider).last()
        if circuit_entry:
            circuit_impact_entry, created = CircuitImpact.objects.get_or_create(
                maintenance=circuit_maintenance_entry, circuit=circuit_entry, defaults={"impact": circuit.impact}
            )
            if created:
                logger.log_success(
                    circuit_impact_entry,
                    message=f"Circuit ID {circuit.circuit_id} linked to Maintenance {maintenance_id}",
                )
        else:
            note_entry, created = Note.objects.get_or_create(
                maintenance=circuit_maintenance_entry,
                title=f"Nonexistent circuit ID {circuit.circuit_id}"[:MAX_NOTE_TITLE_LENGTH],
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
            notification.source.tag_message(logger, notification.msg_id, MessageProcessingStatus.UNKNOWN_CIDS)

    if not CircuitImpact.objects.filter(maintenance=circuit_maintenance_entry):
        logger.log_warning(message=f"Circuit Maintenance {maintenance_id} has none Circuit IDs in the DB.")

    return circuit_maintenance_entry


def update_circuit_maintenance(
    logger: Job,
    notification: MaintenanceNotification,
    circuit_maintenance_entry: CircuitMaintenance,
    parser_maintenance: Maintenance,
    provider: Provider,
):  # pylint: disable=too-many-locals
    """Handles the update of an existent circuit maintenance."""
    maintenance_id = circuit_maintenance_entry.name
    circuit_maintenance_entry.description = parser_maintenance.summary
    if parser_maintenance.status != "NO-CHANGE":
        if parser_maintenance.status in CircuitMaintenanceStatusChoices.values():
            circuit_maintenance_entry.status = parser_maintenance.status
        else:
            circuit_maintenance_entry.status = CircuitMaintenanceStatusChoices.UNKNOWN
    circuit_maintenance_entry.start_time = datetime.datetime.fromtimestamp(
        parser_maintenance.start, tz=datetime.timezone.utc
    )
    circuit_maintenance_entry.end_time = datetime.datetime.fromtimestamp(
        parser_maintenance.end, tz=datetime.timezone.utc
    )
    circuit_maintenance_entry.ack = False
    circuit_maintenance_entry.save()

    circuit_entries = CircuitImpact.objects.filter(maintenance=circuit_maintenance_entry)

    new_cids = {parsed_circuit.circuit_id.lower() for parsed_circuit in parser_maintenance.circuits}
    existing_cids = {circuit_entry.circuit.cid.lower() for circuit_entry in circuit_entries}

    cids_to_update = new_cids & existing_cids
    cids_to_create = new_cids - existing_cids
    cids_to_remove = existing_cids - new_cids

    for cid in cids_to_create:
        circuit_entry = Circuit.objects.filter(cid__iexact=cid, provider=provider.pk).last()
        circuit = [
            parsed_circuit
            for parsed_circuit in parser_maintenance.circuits
            if parsed_circuit.circuit_id.lower() == cid.lower()
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
                title=f"Nonexistent circuit ID {circuit.circuit_id}"[:MAX_NOTE_TITLE_LENGTH],
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
            notification.source.tag_message(logger, notification.msg_id, MessageProcessingStatus.UNKNOWN_CIDS)

    for cid in cids_to_update:
        circuit_entry = Circuit.objects.filter(cid__iexact=cid, provider=provider.pk).last()
        circuitimpact_entry = CircuitImpact.objects.filter(
            circuit=circuit_entry, maintenance=circuit_maintenance_entry
        ).last()
        circuit = [
            parsed_circuit
            for parsed_circuit in parser_maintenance.circuits
            if parsed_circuit.circuit_id.lower() == cid.lower()
        ][0]
        circuitimpact_entry.impact = circuit.impact
        circuitimpact_entry.save()

    for cid in cids_to_remove:
        circuit_entry = Circuit.objects.filter(cid__iexact=cid, provider=provider.pk).last()
        CircuitImpact.objects.filter(circuit=circuit_entry, maintenance=circuit_maintenance_entry).delete()

    logger.log_info(obj=circuit_maintenance_entry, message=f"Updated Circuit Maintenance {maintenance_id}")


def create_or_update_circuit_maintenance(
    logger: Job,
    notification: MaintenanceNotification,
    raw_entry: RawNotification,
    parser_maintenance: Maintenance,
    provider: Provider,
) -> CircuitMaintenance:
    """Processes a Maintenance, creating or updating the related Circuit Maintenance.

    It returns the CircuitMaintenance entry created or updated.
    """
    maintenance_id = f"{raw_entry.provider.slug}-{parser_maintenance.maintenance_id}"[:MAX_MAINTENANCE_NAME_LENGTH]
    try:
        circuit_maintenance_entry = CircuitMaintenance.objects.get(name=maintenance_id)
        # Using the RawNotification.stamp as the reference to sort because it's the one that takes into account the
        # source receving time.
        last_parsed_notification = (
            circuit_maintenance_entry.parsednotification_set.order_by("raw_notification__stamp").reverse().last()
        )

        # If the notification is older than the latest one used to update the CircuitMaintenance, we skip updating it
        parser_maintenance_datetime = datetime.datetime.fromtimestamp(
            parser_maintenance.stamp, tz=datetime.timezone.utc
        )
        if last_parsed_notification and last_parsed_notification.raw_notification.stamp > parser_maintenance_datetime:
            logger.log_debug(
                f"Not updating CircuitMaintenance {maintenance_id} because the notification is from "
                f"{parser_maintenance_datetime}, older than the most recent notification from {last_parsed_notification.raw_notification.stamp}."
            )
            notification.source.tag_message(logger, notification.msg_id, MessageProcessingStatus.OUT_OF_SEQUENCE)
            return circuit_maintenance_entry

        update_circuit_maintenance(logger, notification, circuit_maintenance_entry, parser_maintenance, provider)
    except ObjectDoesNotExist:
        circuit_maintenance_entry = create_circuit_maintenance(
            logger, notification, maintenance_id, parser_maintenance, provider
        )

    return circuit_maintenance_entry


def get_maintenances_from_notification(logger: Job, notification: MaintenanceNotification, provider: Provider):
    """Use the `circuit_maintenance_parser` library to get Maintenances from the notification."""
    provider_type = provider.cf.get("provider_parser_circuit_maintenances", "").lower() or provider.slug

    parser_provider = init_provider(provider_type=provider_type)
    if not parser_provider:
        logger.log_warning(message=f"Notification Parser not found for {notification.provider_type}")
        notification.source.tag_message(logger, notification.msg_id, MessageProcessingStatus.PARSING_FAILED)
        return None

    data_to_process = NotificationData.init_from_email_bytes(notification.raw_payload)
    if not data_to_process:
        logger.log_failure(message=f"Notification data was not accepted by the parser: {notification.raw_payload}")
        notification.source.tag_message(logger, notification.msg_id, MessageProcessingStatus.PARSING_FAILED)
        return None

    try:
        result = parser_provider.get_maintenances(data_to_process)
        notification.source.tag_message(logger, notification.msg_id, MessageProcessingStatus.PARSED)
        if not result:
            logger.log_info(message=f"No maintenance notifications detected in `{notification.subject}`")
            notification.source.tag_message(logger, notification.msg_id, MessageProcessingStatus.IGNORED)
        return result
    except ProviderError:
        tb_str = traceback.format_exc()
        logger.log_failure(message=f"Parsing failed for notification `{notification.subject}`:\n```\n{tb_str}\n```")
        notification.source.tag_message(logger, notification.msg_id, MessageProcessingStatus.PARSING_FAILED)
    except Exception:
        tb_str = traceback.format_exc()
        logger.log_failure(
            message=f"Unexpected exception while parsing notification `{notification.subject}`.\n```\n{tb_str}\n```"
        )
        notification.source.tag_message(logger, notification.msg_id, MessageProcessingStatus.PARSING_FAILED)
    return None


def create_raw_notification(
    logger: Job, notification: MaintenanceNotification, provider: Provider
) -> Optional[RawNotification]:
    """Create a RawNotification.

    If it already exists, we return `None` to signal we are skipping it.
    """
    try:
        raw_entry = RawNotification.objects.get(
            subject=notification.subject[:MAX_NOTIFICATION_SUBJECT_LENGTH],
            provider=provider,
            stamp=parser.parse(notification.date),
        )
        # If the RawNotification was already created, we ignore it.
        if logger.debug:
            logger.log_debug(message=f"Raw notification already existed with ID: {raw_entry.id}")
        return None
    except ObjectDoesNotExist:
        try:
            raw_entry = RawNotification(
                subject=notification.subject[:MAX_NOTIFICATION_SUBJECT_LENGTH],
                provider=provider,
                raw=notification.raw_payload,
                sender=notification.sender[:MAX_NOTIFICATION_SENDER_LENGTH],
                source=NotificationSource.objects.filter(name=notification.source.name).last(),
                stamp=parser.parse(notification.date),
            )
            raw_entry.save()
            logger.log_success(raw_entry, message="Raw notification created.")
        except Exception as exc:
            logger.log_failure(message=f"Raw notification '{notification.subject}' not created because {str(exc)}")
            return None

    return raw_entry


def process_raw_notification(logger: Job, notification: MaintenanceNotification) -> Optional[uuid.UUID]:
    """Processes a raw notification (maybe containing multiple parsed notifications).

    It creates a RawNotification and if it could be parsed, create the corresponding ParsedNotification and the
    related objects. Finally returns the the UUID of the RawNotification modified.
    """
    try:
        provider = Provider.objects.get(slug=notification.provider_type)
    except ObjectDoesNotExist:
        logger.log_warning(
            message=(
                f"Raw notification not created because is referencing to a provider not existent: {notification.provider_type}"
            )
        )
        notification.source.tag_message(logger, notification.msg_id, MessageProcessingStatus.UNKNOWN_PROVIDER)
        return None

    raw_entry = create_raw_notification(logger, notification, provider)
    if not raw_entry:
        return None

    parser_maintenances = get_maintenances_from_notification(logger, notification, provider)
    if not parser_maintenances:
        return raw_entry.id

    for parser_maintenance in parser_maintenances:
        try:
            circuit_maintenance_entry = create_or_update_circuit_maintenance(
                logger, notification, raw_entry, parser_maintenance, provider
            )
            # Update raw notification as properly parsed
            raw_entry.parsed = True
            raw_entry.save()

            # Insert parsed notification in DB
            parsed_entry = ParsedNotification.objects.create(
                maintenance=circuit_maintenance_entry,
                raw_notification=raw_entry,
                json=parser_maintenance.to_json(),
            )
            logger.log_success(parsed_entry, message=f"Saved Parsed Notification for {circuit_maintenance_entry.name}.")

        except Exception:
            tb_str = traceback.format_exc()
            logger.log_failure(
                message=(
                    f"Unexpected exception while handling parsed notification `{notification.subject}`.\n"
                    f"```\n{tb_str}\n```"
                )
            )

    return raw_entry.id


def get_since_reference(logger: Job) -> int:
    """Get the timestamp from the latest processed RawNotification or a reference from config `raw_notification_initial_days_since`."""
    # Latest retrieved notification will limit the scope of notifications to retrieve
    last_raw_notification = RawNotification.objects.last()
    if last_raw_notification:
        since_reference = last_raw_notification.last_updated.timestamp()
    else:
        since_reference = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
            days=PLUGIN_SETTINGS.get("raw_notification_initial_days_since")
        )
        since_reference = int(since_reference.timestamp())
    logger.log_info(message=f"Processing notifications since {since_reference}")
    return since_reference


class HandleCircuitMaintenanceNotifications(Job):
    """Job to handle external circuit maintenance notifications and turn them into Circuit Maintenances."""

    debug = BooleanVar(default=False, description="Enable getting debug Job messages.")

    class Meta:
        """Meta object boilerplate for HandleParsedNotifications."""

        name = "Update Circuit Maintenances"
        description = "Fetch Circuit Maintenance Notifications from Sources and create or update Circuit Maintenances accordingly."

    def run(self, data=None, commit=None) -> List[uuid.UUID]:
        """Fetch notifications, process them and update Circuit Maintenance accordingly."""
        if self.debug is True:
            self.log_debug("Starting Handle Notifications job.")

        notification_sources = NotificationSource.objects.all()
        if not notification_sources:
            self.log_warning(message="No notification sources configured to retrieve notifications from.")
            return []

        try:
            notifications = get_notifications(
                job_logger=self,
                notification_sources=notification_sources,
                since=get_since_reference(self),
            )
        except Exception as error:
            self.log_failure(
                message=f"Unexpected exception when retrieving notifications from sources ({notification_sources}): {error}"
            )
            return []

        if not notifications:
            self.log_info(message="No notifications received.")
            return []

        raw_notification_ids = []
        for notification in notifications:
            self.log_info(message=f"Processing notification `{notification.subject}`.")
            try:
                raw_id = process_raw_notification(self, notification)
                if raw_id:
                    raw_notification_ids.append(raw_id)
            except Exception as error:
                self.log_failure(message=f"Unexpected exception when parsing notifications: {error}")

        if self.debug is True:
            self.log_debug(f"{len(raw_notification_ids)} notifications processed.")

        return raw_notification_ids
