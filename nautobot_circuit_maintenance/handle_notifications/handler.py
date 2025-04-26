# pylint: disable=logging-fstring-interpolation
"""Notifications jobs."""

import datetime
import uuid
from typing import List, Optional

from circuit_maintenance_parser import Maintenance, NotificationData, ProviderError, init_provider
from dateutil import parser
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from nautobot.circuits.models import Circuit, Provider
from nautobot.extras.jobs import DryRunVar, Job

from nautobot_circuit_maintenance.choices import CircuitMaintenanceStatusChoices
from nautobot_circuit_maintenance.enum import MessageProcessingStatus
from nautobot_circuit_maintenance.models import (
    MAX_MAINTENANCE_NAME_LENGTH,
    MAX_NOTE_TITLE_LENGTH,
    MAX_NOTIFICATION_SENDER_LENGTH,
    MAX_NOTIFICATION_SUBJECT_LENGTH,
    CircuitImpact,
    CircuitMaintenance,
    Note,
    NotificationSource,
    ParsedNotification,
    RawNotification,
)

from .sources import MaintenanceNotification, get_notifications

name = "Circuit Maintenance"  # pylint: disable=invalid-name

# pylint: disable=broad-except
PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("nautobot_circuit_maintenance", {})


def create_circuit_maintenance(
    job: Job,
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
    job.logger.info("Created Circuit Maintenance.", extra={"object": circuit_maintenance_entry})

    for circuit in parser_maintenance.circuits:
        circuit_entry = Circuit.objects.filter(cid__iexact=circuit.circuit_id, provider=provider).last()
        if circuit_entry:
            circuit_impact_entry, created = CircuitImpact.objects.get_or_create(
                maintenance=circuit_maintenance_entry, circuit=circuit_entry, defaults={"impact": circuit.impact}
            )
            if created:
                job.logger.info(
                    f"Circuit ID {circuit.circuit_id} linked to Maintenance {maintenance_id}",
                    extra={"object": circuit_impact_entry},
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
                job.logger.warning(
                    f"Circuit ID {circuit.circuit_id} referenced in {maintenance_id} is not in the Database, adding a note",
                    extra={"object": note_entry},
                )
            notification.source.tag_message(job, notification.msg_id, MessageProcessingStatus.UNKNOWN_CIDS)

    if not CircuitImpact.objects.filter(maintenance=circuit_maintenance_entry):
        job.logger.warning(
            "Circuit Maintenance has none Circuit IDs in the DB.", extra={"object": circuit_maintenance_entry}
        )

    return circuit_maintenance_entry


def update_circuit_maintenance(
    job: Job,
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
            job.logger.info(
                f"Circuit ID {circuit.circuit_id} linked to Maintenance {maintenance_id}",
                extra={"object": circuit_impact_entry},
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
                job.logger.warning(
                    f"Circuit ID {circuit.circuit_id} referenced in {maintenance_id} is not in the Database, adding a note",
                    extra={"object": note_entry},
                )
            notification.source.tag_message(job, notification.msg_id, MessageProcessingStatus.UNKNOWN_CIDS)

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

    job.logger.info(
        f"Updated Circuit Maintenance {maintenance_id}",
        extra={"object": circuit_maintenance_entry},
    )


def create_or_update_circuit_maintenance(
    job: Job,
    notification: MaintenanceNotification,
    raw_entry: RawNotification,
    parser_maintenance: Maintenance,
    provider: Provider,
) -> CircuitMaintenance:
    """Processes a Maintenance, creating or updating the related Circuit Maintenance.

    It returns the CircuitMaintenance entry created or updated.
    """
    maintenance_id = f"{raw_entry.provider.name}-{parser_maintenance.maintenance_id}"[:MAX_MAINTENANCE_NAME_LENGTH]
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
            job.logger.debug(
                f"Not updating CircuitMaintenance {maintenance_id} because the notification is from "
                f"{parser_maintenance_datetime}, older than the most recent notification from {last_parsed_notification.raw_notification.stamp}.",
                extra={"object": circuit_maintenance_entry},
            )
            notification.source.tag_message(job, notification.msg_id, MessageProcessingStatus.OUT_OF_SEQUENCE)
            return circuit_maintenance_entry

        update_circuit_maintenance(job, notification, circuit_maintenance_entry, parser_maintenance, provider)
    except ObjectDoesNotExist:
        circuit_maintenance_entry = create_circuit_maintenance(
            job, notification, maintenance_id, parser_maintenance, provider
        )

    return circuit_maintenance_entry


def get_maintenances_from_notification(job: Job, notification: MaintenanceNotification, provider: Provider):
    """Use the `circuit_maintenance_parser` library to get Maintenances from the notification."""
    provider_type = provider.cf.get("provider_parser_circuit_maintenances", "").lower() or provider.name

    parser_provider = init_provider(provider_type=provider_type)
    if not parser_provider:
        job.logger.warning(
            f"Notification Parser not found for {notification.provider_type}", extra={"object": notification}
        )
        notification.source.tag_message(job, notification.msg_id, MessageProcessingStatus.PARSING_FAILED)
        return None

    data_to_process = NotificationData.init_from_email_bytes(notification.raw_payload)
    if not data_to_process:
        job.logger.error(
            "Notification data was not accepted by the parser: {notification.raw_payload}",
            extra={"object": notification},
        )
        notification.source.tag_message(job, notification.msg_id, MessageProcessingStatus.PARSING_FAILED)
        raise ValueError("Notification data was not accepted by the parser")

    try:
        result = parser_provider.get_maintenances(data_to_process)
        notification.source.tag_message(job, notification.msg_id, MessageProcessingStatus.PARSED)
        if not result:
            job.logger.info(
                f"No maintenance notifications detected in `{notification.subject}`",
                extra={"object": notification},
            )
            notification.source.tag_message(job, notification.msg_id, MessageProcessingStatus.IGNORED)
        return result
    except ProviderError:
        job.logger.error(
            "Parsing failed for notification",
            extra={"object": notification},
            exc_info=True,
        )
        notification.source.tag_message(job, notification.msg_id, MessageProcessingStatus.PARSING_FAILED)
        raise
    except Exception:
        job.logger.error(
            "Unexpected exception while parsing notification",
            extra={"object": notification},
            exc_info=True,
        )
        notification.source.tag_message(job, notification.msg_id, MessageProcessingStatus.PARSING_FAILED)
        raise


def create_raw_notification(
    job: Job,
    notification: MaintenanceNotification,
    provider: Provider,
) -> RawNotification:
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
        job.logger.debug(f"Raw notification already existed with ID: {raw_entry.id}", extra={"object": raw_entry})
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
            job.logger.info("Raw notification created.", extra={"object": raw_entry})
        except Exception:
            job.logger.error(
                f"Raw notification '{notification.subject}' not created",
                extra={"object": notification},
                exc_info=True,
            )
            raise

    return raw_entry


def process_raw_notification(job: Job, notification: MaintenanceNotification) -> Optional[uuid.UUID]:
    """Processes a raw notification (maybe containing multiple parsed notifications).

    It creates a RawNotification and if it could be parsed, create the corresponding ParsedNotification and the
    related objects. Finally returns the the UUID of the RawNotification modified.
    """
    try:
        provider = Provider.objects.get_by_natural_key(notification.provider_type)
    except ObjectDoesNotExist:
        job.logger.warning(
            "Raw notification not created because is referencing to a provider not existent.",
            extra={"object": notification},
        )
        notification.source.tag_message(job, notification.msg_id, MessageProcessingStatus.UNKNOWN_PROVIDER)
        return None

    raw_entry = create_raw_notification(job, notification, provider)
    if not raw_entry:
        return None

    parser_maintenances = get_maintenances_from_notification(job, notification, provider)
    if not parser_maintenances:
        return raw_entry.id

    for parser_maintenance in parser_maintenances:
        try:
            circuit_maintenance_entry = create_or_update_circuit_maintenance(
                job, notification, raw_entry, parser_maintenance, provider
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
            parsed_entry.save()
            job.logger.info(
                f"Saved Parsed Notification for {circuit_maintenance_entry.name}.",
                extra={"object": parsed_entry},
            )

        except Exception:
            job.logger.error(
                "Unexpected exception while handling parsed notification",
                extra={"object": notification},
                exc_info=True,
            )
            raise

    return raw_entry.id


def get_since_reference(job: Job) -> int:
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
    job.logger.info(f"Processing notifications since {since_reference}", extra={"object": last_raw_notification})
    return since_reference


class DryRunTransactionSkip(Exception):
    """Exception to handle dryrun mode."""


class HandleCircuitMaintenanceNotifications(Job):
    """Job to handle external circuit maintenance notifications and turn them into Circuit Maintenances."""

    dryrun = DryRunVar()

    class Meta:
        """Meta object boilerplate for HandleParsedNotifications."""

        name = "Update Circuit Maintenances"
        has_sensitive_variables = False
        description = "Fetch Circuit Maintenance Notifications from Sources and create or update Circuit Maintenances accordingly."

    # pylint: disable=arguments-differ
    def run(self, dryrun=False) -> List[uuid.UUID]:
        """Fetch notifications, process them and update Circuit Maintenance accordingly."""
        self.logger.debug("Starting Handle Notifications job.")

        notification_sources = NotificationSource.objects.all()
        if not notification_sources:
            self.logger.warning("No notification sources configured to retrieve notifications from.")
            return []

        try:
            notifications = get_notifications(
                job=self,
                notification_sources=notification_sources,
                since=get_since_reference(self),
            )
        except Exception:
            self.logger.error(
                f"Unexpected exception when retrieving notifications from sources ({notification_sources})",
                exc_info=True,
            )
            raise

        if not notifications:
            self.logger.info("No notifications received.")
            return []

        raw_notification_ids = []
        for notification in notifications:
            self.logger.info(
                f"Processing notification `{notification.subject}` with ID `{notification.msg_id}` from source `{notification.source.name}`."
            )
            try:
                with transaction.atomic():
                    raw_id = process_raw_notification(self, notification)
                    if raw_id:
                        raw_notification_ids.append(raw_id)
                    if dryrun:
                        raise DryRunTransactionSkip()
            except DryRunTransactionSkip:
                self.logger.info("DRYRUN mode, nothing has been committed.")
            except Exception:
                self.logger.error(
                    "Unexpected exception when parsing notifications",
                    extra={"object": notification},
                    exc_info=True,
                )

        self.logger.info(f"{len(raw_notification_ids)} notifications processed.")

        return raw_notification_ids
