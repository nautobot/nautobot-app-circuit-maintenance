"""Tests for Handle Notifications methods."""
import uuid
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import format_datetime
from django.test import TestCase
from jinja2 import Template
from nautobot.circuits.models import Circuit, Provider
from circuit_maintenance_parser import init_provider, NotificationData

from nautobot_circuit_maintenance.handle_notifications.handler import (
    create_circuit_maintenance,
    get_maintenances_from_notification,
    get_since_reference,
    HandleCircuitMaintenanceNotifications,
    process_raw_notification,
    update_circuit_maintenance,
)

from nautobot_circuit_maintenance.models import (
    CircuitMaintenance,
    CircuitImpact,
    MAX_MAINTENANCE_NAME_LENGTH,
    MAX_NOTIFICATION_SENDER_LENGTH,
    MAX_NOTIFICATION_SUBJECT_LENGTH,
    NotificationSource,
    Note,
    RawNotification,
    ParsedNotification,
)
from nautobot_circuit_maintenance.handle_notifications.sources import MaintenanceNotification, Source


def generate_email_notification(notification_data: dict, source: Source):
    """Generate email notification text for a provider."""
    raw_notification_template = """
BEGIN:VCALENDAR
PRODID:Data::ICal 0.16
VERSION:2.0
BEGIN:VEVENT
DESCRIPTION:{{ obj.provider }} URGENT Maintenance Notification: {{ obj.status }} [{{ obj.name }}] Please refer to the email notification for more details regarding maintenance or outage reason and impact.
DTEND:20210808T071300Z
DTSTAMP:{{ obj.stamp.strftime("%Y%m%dT%H%M%SZ") }}
DTSTART:20210808T050000Z
SEQUENCE:1
SUMMARY:{{ obj.provider }} URGENT Maintenance Notification: {{ obj.status }} [{{ obj.name }}]
UID:{{ obj.name }}
X-MAINTNOTE-ACCOUNT:{{ obj.account }}
X-MAINTNOTE-IMPACT:OUTAGE
X-MAINTNOTE-MAINTENANCE-ID:{{ obj.name }}
{% for circuitimpact in obj.circuitimpacts -%}
X-MAINTNOTE-OBJECT-ID;X-MAINTNOTE-OBJECT-IMPACT={{ circuitimpact.impact }}:{{ circuitimpact.cid }}
{% endfor -%}
X-MAINTNOTE-PROVIDER:{{ obj.provider }}
X-MAINTNOTE-STATUS:{{ obj.status }}
END:VEVENT
END:VCALENDAR
"""

    template = Template(raw_notification_template)
    email_message = EmailMessage()
    email_message["From"] = "Sender <sender@example.com>"
    email_message["Date"] = format_datetime(notification_data["stamp"])
    email_message["Subject"] = "Test subject " + "1234567890" * 20
    email_message["Content-Type"] = "text/calendar"
    email_message.set_payload(template.render(obj=notification_data).encode("utf-8"))

    return MaintenanceNotification(
        msg_id=b"12345",
        subject="Test subject " + "1234567890" * 20,
        sender="sender@example.com",
        source=source,
        raw_payload=email_message.as_bytes(),
        provider_type=notification_data["provider"],
        date=format_datetime(notification_data["stamp"]),
    )


def get_base_notification_data(provider_slug="ntt") -> dict:
    """Provides a dictionary of notification data to build notifications."""
    provider = Provider.objects.get(slug=provider_slug)

    notification_data = {
        "provider": provider.slug,
        "account": f"ACC-{provider.slug.upper()}",
        "name": f"MNT-{provider.slug.upper()}",
        "status": "CONFIRMED",
        "circuitimpacts": [],
        "stamp": datetime(2021, 2, 1, 9, 33, 34, tzinfo=timezone.utc),
    }

    sample_circuits = Circuit.objects.filter(provider=provider)
    for circuit in sample_circuits:
        # Intentionally convert the CID reference to lower-case,
        # because all of our circuit lookups *should* be case-insensitive
        notification_data["circuitimpacts"].append({"cid": circuit.cid.lower(), "impact": "NO-IMPACT"})

    return notification_data


class TestHandleNotificationsJob(TestCase):  # pylint: disable=too-many-public-methods
    """Test case for all the related methods in Handle Notifications."""

    fixtures = ["handle_notifications_job.yaml"]
    job = HandleCircuitMaintenanceNotifications()
    job.debug = True
    job._job_result = Mock()  # pylint: disable=protected-access
    job.log_debug = Mock()
    job.log_info = Mock()
    job.log_warning = Mock()
    job.log_failure = Mock()
    job.log_success = Mock()

    def setUp(self):
        self.notification_source = NotificationSource.objects.create(name="whatever 1", slug="whatever-1")
        self.source = Source(name=self.notification_source.name, url="http://example.com")

    def test_run_simple(self):
        """Test the simple execution to create a Circuit Maintenance."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source)

        with patch(
            "nautobot_circuit_maintenance.handle_notifications.handler.get_notifications"
        ) as mock_get_notifications, patch(
            "nautobot_circuit_maintenance.handle_notifications.sources.Source.tag_message"
        ) as mock_tag_message:
            mock_get_notifications.return_value = [test_notification]
            processed_notifications = self.job.run(commit=True)

            mock_get_notifications.assert_called_once()
            self.assertEqual(1, len(processed_notifications))
            self.assertEqual(1, len(RawNotification.objects.all()))
            self.assertEqual(1, len(ParsedNotification.objects.all()))
            self.assertEqual(1, len(CircuitMaintenance.objects.all()))
            self.assertEqual(2, len(CircuitImpact.objects.all()))
            self.assertEqual(0, len(Note.objects.all()))
            mock_tag_message.assert_called_with(self.job, test_notification.msg_id, "parsed")
            self.job.log_debug.assert_called_with("1 notifications processed.")

    def test_run_nonexistent_circuit(self):
        """Test when a Notification contains a nonexistent circuit."""
        notification_data = get_base_notification_data()
        fake_cid = "nonexistent circuit"
        notification_data["circuitimpacts"].append({"cid": fake_cid, "impact": "NO-IMPACT"})
        test_notification = generate_email_notification(notification_data, self.source)

        with patch(
            "nautobot_circuit_maintenance.handle_notifications.handler.get_notifications"
        ) as mock_get_notifications, patch(
            "nautobot_circuit_maintenance.handle_notifications.sources.Source.tag_message"
        ) as mock_tag_message:
            mock_get_notifications.return_value = [test_notification]
            processed_notifications = self.job.run(commit=True)

            mock_get_notifications.assert_called_once()
            self.assertEqual(1, len(processed_notifications))
            self.assertEqual(1, len(RawNotification.objects.all()))
            self.assertEqual(1, len(ParsedNotification.objects.all()))
            self.assertEqual(1, len(CircuitMaintenance.objects.all()))
            self.assertEqual(2, len(CircuitImpact.objects.all()))
            self.assertEqual(1, len(Note.objects.all()))
            self.assertIn(fake_cid, Note.objects.all().first().title)
            mock_tag_message.assert_any_call(self.job, test_notification.msg_id, "parsed")
            mock_tag_message.assert_any_call(self.job, test_notification.msg_id, "unknown-cids")
            self.job.log_debug.assert_called_with("1 notifications processed.")

            # Do some checking of string representation length for potential change-logging issues
            # (ObjectChange.object_repr field has a limit of 200 characters)
            for model in (
                RawNotification,
                ParsedNotification,
                CircuitMaintenance,
                CircuitImpact,
                Note,
            ):
                objectchange = model.objects.first().to_objectchange("create")
                objectchange.request_id = uuid.uuid4()
                objectchange.save()
                self.assertLessEqual(len(str(model.objects.first())), 200)

    def test_run_no_notifications(self):
        """Test when a there are no notifications."""

        with patch(
            "nautobot_circuit_maintenance.handle_notifications.handler.get_notifications"
        ) as mock_get_notifications:
            mock_get_notifications.return_value = []
            processed_notifications = self.job.run(commit=True)

            mock_get_notifications.assert_called_once()
            self.assertEqual(0, len(processed_notifications))
            self.assertEqual(0, len(RawNotification.objects.all()))
            self.assertEqual(0, len(ParsedNotification.objects.all()))
            self.assertEqual(0, len(CircuitMaintenance.objects.all()))
            self.assertEqual(0, len(CircuitImpact.objects.all()))
            self.assertEqual(0, len(Note.objects.all()))
            self.job.log_info.assert_called_with(message="No notifications received.")

    def test_run_no_notification_source(self):
        """Test when a there are no Notification Sources."""

        NotificationSource.objects.all().delete()
        processed_notifications = self.job.run(commit=True)
        self.assertEqual(0, len(processed_notifications))
        self.job.log_warning.assert_called_with(
            message="No notification sources configured to retrieve notifications from."
        )

    def test_run_invalid_notification(self):
        """Test when a there is an invalid notification."""

        notification_data = get_base_notification_data()
        notification_data["status"] = "Non valid status"
        test_notification = generate_email_notification(notification_data, self.source)

        with patch(
            "nautobot_circuit_maintenance.handle_notifications.handler.get_notifications"
        ) as mock_get_notifications, patch(
            "nautobot_circuit_maintenance.handle_notifications.sources.Source.tag_message"
        ) as mock_tag_message:
            mock_get_notifications.return_value = [test_notification]
            processed_notifications = self.job.run(commit=True)

            mock_get_notifications.assert_called_once()
            self.assertEqual(1, len(processed_notifications))
            self.assertEqual(1, len(RawNotification.objects.all()))
            self.assertEqual(0, len(ParsedNotification.objects.all()))
            self.assertEqual(0, len(CircuitMaintenance.objects.all()))
            self.assertEqual(0, len(CircuitImpact.objects.all()))
            self.assertEqual(0, len(Note.objects.all()))
            mock_tag_message.assert_called_with(self.job, test_notification.msg_id, "parsing-failed")
            self.job.log_warning.assert_called()
            self.job.log_debug.assert_called_with("1 notifications processed.")

    def test_process_raw_notification_no_provider_in_parser(self):
        """Test process_raw_notification with non existant Provider in the parser library."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source)
        test_notification.provider_type = "abc"
        with patch("nautobot_circuit_maintenance.handle_notifications.sources.Source.tag_message") as mock_tag_message:
            res = process_raw_notification(self.job, test_notification)

        self.assertNotEqual(res, None)
        mock_tag_message.assert_called_with(self.job, test_notification.msg_id, "parsing-failed")
        self.job.log_warning.assert_called_with(
            message=f"Notification Parser not found for {test_notification.provider_type}"
        )

    def test_process_raw_notification_no_provider_in_plugin(self):
        """Test process_raw_notification with non existant provider in the Plugin."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source)
        test_notification.provider_type = "telstra"
        with patch("nautobot_circuit_maintenance.handle_notifications.sources.Source.tag_message") as mock_tag_message:
            res = process_raw_notification(self.job, test_notification)

        self.assertEqual(res, None)
        mock_tag_message.assert_called_with(self.job, test_notification.msg_id, "unknown-provider")
        self.job.log_warning.assert_called_with(
            message=f"Raw notification not created because is referencing to a provider not existent: {test_notification.provider_type}"
        )

    def test_process_raw_notification(self):
        """Test process_raw_notification."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source)
        res = process_raw_notification(self.job, test_notification)

        raw_notification = RawNotification.objects.get(pk=res)
        self.assertEqual(raw_notification.pk, res)
        self.assertEqual(raw_notification.parsed, True)
        self.assertEqual(1, len(ParsedNotification.objects.all()))
        self.job.log_success.assert_any_call(raw_notification, message="Raw notification created.")

    def test_process_raw_notification_duplicated_issue(self):
        """Test process_raw_notification duplicated."""
        self.test_process_raw_notification()
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source)

        # A duplicated RawNotification skip creation
        res = process_raw_notification(self.job, test_notification)
        self.assertEqual(res, None)
        self.assertIn("Raw notification already existed with ID", str(self.job.log_debug.call_args))

        # After a duplicated RawNotification, a new RawNotification should be inserted
        test_notification.subject = "another_subject"
        res = process_raw_notification(self.job, test_notification)
        raw_notification = RawNotification.objects.get(pk=res)
        self.assertEqual(raw_notification.pk, res)

    def test_process_raw_notification_parser_issue(self):
        """Test process_raw_notification with parsing issues"""
        notification_data = get_base_notification_data()
        notification_data["status"] = "Non valid status"
        test_notification = generate_email_notification(notification_data, self.source)
        with patch("nautobot_circuit_maintenance.handle_notifications.sources.Source.tag_message") as mock_tag_message:
            res = process_raw_notification(self.job, test_notification)

        raw_notification = RawNotification.objects.get(pk=res)
        self.assertEqual(raw_notification.pk, res)
        self.assertEqual(raw_notification.parsed, False)
        self.assertEqual(0, len(ParsedNotification.objects.all()))
        mock_tag_message.assert_called_with(self.job, test_notification.msg_id, "parsing-failed")
        self.job.log_success.assert_any_call(raw_notification, message="Raw notification created.")
        self.job.log_warning.assert_called()

    def test_get_maintenances_from_notification(self):
        """Test get_maintenances_from_notification."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source)
        provider = Provider.objects.get(slug=test_notification.provider_type)
        with patch("nautobot_circuit_maintenance.handle_notifications.sources.Source.tag_message") as mock_tag_message:
            parser_maintenances = get_maintenances_from_notification(self.job, test_notification, provider)

        self.assertEqual(1, len(parser_maintenances))
        mock_tag_message.assert_called_with(self.job, test_notification.msg_id, "parsed")

    def test_get_maintenances_from_notification_wrong_data(self):
        """Test get_maintenances_from_notification."""
        notification_data = get_base_notification_data()
        notification_data["status"] = "Non valid status"
        test_notification = generate_email_notification(notification_data, self.source)
        provider = Provider.objects.get(slug=test_notification.provider_type)
        with patch("nautobot_circuit_maintenance.handle_notifications.sources.Source.tag_message") as mock_tag_message:
            parser_maintenances = get_maintenances_from_notification(self.job, test_notification, provider)

        self.assertIsNone(parser_maintenances)
        mock_tag_message.assert_called_with(self.job, test_notification.msg_id, "parsing-failed")
        self.job.log_failure.assert_called()

    def test_get_maintenances_from_notification_non_existent_provider_in_parser(self):
        """Test get_maintenances_from_notification."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source)
        provider = Provider.objects.get(slug=test_notification.provider_type)
        provider.cf["provider_parser_circuit_maintenances"] = "unkown_provider_in_parser"
        with patch("nautobot_circuit_maintenance.handle_notifications.sources.Source.tag_message") as mock_tag_message:
            parser_maintenances = get_maintenances_from_notification(self.job, test_notification, provider)

        self.assertIsNone(parser_maintenances)
        mock_tag_message.assert_called_with(self.job, test_notification.msg_id, "parsing-failed")
        self.job.log_warning.assert_any_call(message=f"Notification Parser not found for {provider.slug}")

    def test_create_circuit_maintenance(self):
        """Test create_circuit_maintenance."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source)
        provider = Provider.objects.get(slug=test_notification.provider_type)
        RawNotification.objects.get_or_create(
            subject=test_notification.subject[:MAX_NOTIFICATION_SUBJECT_LENGTH],
            provider=provider,
            raw=test_notification.raw_payload,
            sender=test_notification.sender,
            source=self.notification_source,
            stamp=datetime.now(timezone.utc),
        )
        parser_provider = init_provider(provider_type=test_notification.provider_type)
        data_to_process = NotificationData.init_from_email_bytes(test_notification.raw_payload)
        parsed_maintenance = parser_provider.get_maintenances(data_to_process)[0]
        create_circuit_maintenance(
            self.job,
            test_notification,
            f"{provider.slug}-{parsed_maintenance.maintenance_id}",
            parsed_maintenance,
            provider,
        )
        self.assertEqual(1, len(CircuitMaintenance.objects.all()))
        self.assertEqual(2, len(CircuitImpact.objects.all()))
        self.assertEqual(0, len(Note.objects.all()))

    def test_create_circuit_maintenance_no_circuits(self):
        """Test create_circuit_maintenance without existent circuits."""
        notification_data = get_base_notification_data()
        notification_data["circuitimpacts"] = [{"cid": "nonexistent", "impact": "NO-IMPACT"}]
        test_notification = generate_email_notification(notification_data, self.source)
        provider = Provider.objects.get(slug=test_notification.provider_type)
        RawNotification.objects.get_or_create(
            subject=test_notification.subject[:MAX_NOTIFICATION_SUBJECT_LENGTH],
            provider=provider,
            raw=test_notification.raw_payload,
            sender=test_notification.sender,
            source=self.notification_source,
            stamp=datetime.now(timezone.utc),
        )
        parser_provider = init_provider(provider_type=test_notification.provider_type)
        data_to_process = NotificationData.init_from_email_bytes(test_notification.raw_payload)
        parsed_maintenance = parser_provider.get_maintenances(data_to_process)[0]
        with patch("nautobot_circuit_maintenance.handle_notifications.sources.Source.tag_message") as mock_tag_message:
            create_circuit_maintenance(
                self.job,
                test_notification,
                f"{provider.slug}-{parsed_maintenance.maintenance_id}",
                parsed_maintenance,
                provider,
            )

        self.assertEqual(1, len(CircuitMaintenance.objects.all()))
        self.assertEqual(0, len(CircuitImpact.objects.all()))
        self.assertEqual(1, len(Note.objects.all()))
        mock_tag_message.assert_called_with(self.job, test_notification.msg_id, "unknown-cids")

    def test_create_circuit_maintenance_unknown_status(self):
        """Test create_circuit_maintenance with an unknown status."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source)
        provider = Provider.objects.get(slug=test_notification.provider_type)
        RawNotification.objects.get_or_create(
            subject=test_notification.subject[:MAX_NOTIFICATION_SUBJECT_LENGTH],
            provider=provider,
            raw=test_notification.raw_payload,
            sender=test_notification.sender,
            source=self.notification_source,
            stamp=datetime.now(timezone.utc),
        )
        parser_provider = init_provider(provider_type=test_notification.provider_type)
        data_to_process = NotificationData.init_from_email_bytes(test_notification.raw_payload)
        parsed_maintenance = parser_provider.get_maintenances(data_to_process)[0]
        parsed_maintenance.status = "No idea!"
        create_circuit_maintenance(
            self.job,
            test_notification,
            f"{provider.slug}-{parsed_maintenance.maintenance_id}",
            parsed_maintenance,
            provider,
        )

        self.assertEqual(1, len(CircuitMaintenance.objects.all()))
        self.assertEqual(2, len(CircuitImpact.objects.all()))
        self.assertEqual(0, len(Note.objects.all()))

        self.assertEqual("UNKNOWN", CircuitMaintenance.objects.first().status)

    def test_update_circuit_maintenance(self):
        """Test update_circuit_maintenance."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source)
        provider = Provider.objects.get(slug=test_notification.provider_type)
        with patch(
            "nautobot_circuit_maintenance.handle_notifications.handler.get_notifications"
        ) as mock_get_notifications:
            mock_get_notifications.return_value = [test_notification]
            self.job.run(commit=True)

        # Adding changes
        notification_data["status"] = "COMPLETED"
        circuit_to_update = notification_data["circuitimpacts"].pop()
        notification_data["circuitimpacts"].pop()
        notification_data["circuitimpacts"].append({"cid": "nonexistent", "impact": "NO-IMPACT"})
        circuit_to_update["impact"] = "OUTAGE"
        notification_data["circuitimpacts"].append(circuit_to_update)
        test_notification = generate_email_notification(notification_data, self.source)
        parser_provider = init_provider(provider_type=test_notification.provider_type)
        data_to_process = NotificationData.init_from_email_bytes(test_notification.raw_payload)
        parsed_maintenance = parser_provider.get_maintenances(data_to_process)[0]
        maintenance_id = f"{provider.slug}-{parsed_maintenance.maintenance_id}"
        circuit_maintenance_entry = CircuitMaintenance.objects.get(name=maintenance_id)
        update_circuit_maintenance(self.job, test_notification, circuit_maintenance_entry, parsed_maintenance, provider)
        self.assertEqual(1, len(CircuitMaintenance.objects.all()))
        self.assertEqual(1, len(CircuitImpact.objects.all()))
        self.assertEqual(1, len(Note.objects.all()))
        circuit_maintenance_entry = CircuitMaintenance.objects.get(name=maintenance_id)
        self.assertEqual(notification_data["status"], circuit_maintenance_entry.status)
        circuit_impact_entry = CircuitImpact.objects.get(circuit__cid__iexact=circuit_to_update["cid"])
        self.assertEqual(circuit_to_update["impact"], circuit_impact_entry.impact)

    def test_update_circuit_maintenance_unordered_notifications(self):
        """Test update_circuit_maintenance with unordered notifications."""
        notification_data = get_base_notification_data()
        test_notification_older = generate_email_notification(notification_data, self.source)

        notification_data["status"] = "COMPLETED"
        notification_data["stamp"] = datetime(2021, 2, 2, 9, 33, 34, tzinfo=timezone.utc)
        test_notification_newer = generate_email_notification(notification_data, self.source)

        provider = Provider.objects.get(slug=test_notification_older.provider_type)
        with patch(
            "nautobot_circuit_maintenance.handle_notifications.handler.get_notifications"
        ) as mock_get_notifications, patch(
            "nautobot_circuit_maintenance.handle_notifications.sources.Source.tag_message"
        ) as mock_tag_message:
            # We simulate that the newer notifications are retrieved first, so processed first
            mock_get_notifications.return_value = [test_notification_newer, test_notification_older]
            self.job.run(commit=True)

        # Verify that both notifications where related to same CircuitMaintenance
        self.assertEqual(1, len(CircuitMaintenance.objects.all()))

        mock_tag_message.assert_called_with(self.job, test_notification_older.msg_id, "out-of-sequence")

        maintenance_id = f"{provider.slug}-{notification_data['name']}"
        circuit_maintenance_entry = CircuitMaintenance.objects.get(name=maintenance_id)
        # Verify that the final status of the CircuitMaintenance depends on the newest notification
        self.assertEqual(circuit_maintenance_entry.status, "COMPLETED")
        # Verify that both parsed notifications are linked to the CircuitMaintenance for future reference
        self.assertEqual(len(circuit_maintenance_entry.parsednotification_set.all()), 2)

    def test_update_circuit_maintenance_status_no_change(self):
        """Test update_circuit_maintenance with a "NO-CHANGE" status value."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source)
        provider = Provider.objects.get(slug=test_notification.provider_type)
        with patch(
            "nautobot_circuit_maintenance.handle_notifications.handler.get_notifications"
        ) as mock_get_notifications:
            mock_get_notifications.return_value = [test_notification]
            self.job.run(commit=True)

        # Adding changes
        parser_provider = init_provider(provider_type=test_notification.provider_type)
        data_to_process = NotificationData.init_from_email_bytes(test_notification.raw_payload)
        parsed_maintenance = parser_provider.get_maintenances(data_to_process)[0]
        parsed_maintenance.status = "NO-CHANGE"
        maintenance_id = f"{provider.slug}-{parsed_maintenance.maintenance_id}"
        circuit_maintenance_entry = CircuitMaintenance.objects.get(name=maintenance_id)

        update_circuit_maintenance(self.job, test_notification, circuit_maintenance_entry, parsed_maintenance, provider)

        circuit_maintenance_entry = CircuitMaintenance.objects.get(name=maintenance_id)
        # Status should not be changed:
        self.assertEqual("CONFIRMED", circuit_maintenance_entry.status)

    def test_create_or_update_circuit_maintenance_truncated_fields(self):
        """Test create_or_update_circuit_maintenance with long fields that must be truncated to fit the DB."""
        notification_data = get_base_notification_data()
        notification_data["name"] = f"MNT-{'1234567890' * 20}"
        test_notification = generate_email_notification(notification_data, self.source)
        test_notification.subject = "abcdefghijiklmnopqrstuvwxyz " * 10
        test_notification.sender = f"{'abcdefghij' * 20}@example.com"

        notification_data["status"] = "COMPLETED"
        notification_data["stamp"] = datetime(2021, 2, 2, 9, 33, 34, tzinfo=timezone.utc)
        test_notification_newer = generate_email_notification(notification_data, self.source)
        test_notification_newer.subject = "abcdefghijiklmnopqrstuvwxyz " * 10
        test_notification_newer.sender = f"{'abcdefghij' * 20}@example.com"
        provider = Provider.objects.get(slug=test_notification.provider_type)
        with patch("nautobot_circuit_maintenance.handle_notifications.handler.get_notifications") as mock_get_notif:
            mock_get_notif.return_value = [test_notification, test_notification_newer]
            self.job.run(commit=True)

        # Make sure raw notification sender and subject were correctly truncated
        self.assertEqual(2, len(RawNotification.objects.all()))
        for raw_notification in RawNotification.objects.filter(provider=provider):
            self.assertEqual(MAX_NOTIFICATION_SENDER_LENGTH, len(raw_notification.sender))
            self.assertEqual(test_notification.sender[:MAX_NOTIFICATION_SENDER_LENGTH], raw_notification.sender)
            self.assertEqual(MAX_NOTIFICATION_SUBJECT_LENGTH, len(raw_notification.subject))
            self.assertEqual(test_notification.subject[:MAX_NOTIFICATION_SENDER_LENGTH], raw_notification.subject)

        # Make sure maintenance name was correctly truncated on both create and update
        maintenance_id = f"{provider.slug}-{notification_data['name']}"[:MAX_MAINTENANCE_NAME_LENGTH]
        self.assertEqual(MAX_MAINTENANCE_NAME_LENGTH, len(maintenance_id))
        self.assertEqual(1, len(CircuitMaintenance.objects.all()))
        circuit_maintenance_entry = CircuitMaintenance.objects.get(name=maintenance_id)
        self.assertEqual("COMPLETED", circuit_maintenance_entry.status)
        # Verify that both parsed notifications are linked to the CircuitMaintenance for future reference
        self.assertEqual(len(circuit_maintenance_entry.parsednotification_set.all()), 2)

    def test_get_since_with_previous_raw_notification(self):
        """Test get_since_reference with a previous raw_notification."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source)
        raw_id = process_raw_notification(self.job, test_notification)
        since_reference = get_since_reference(self.job)
        self.assertEqual(since_reference, RawNotification.objects.get(id=raw_id).last_updated.timestamp())

    def test_update_circuit_maintenance_with_duplicated_notes(self):
        """Test update_circuit_maintenance with duplicated notes."""
        notification_data = get_base_notification_data()
        # Updating the circuit impact to reference to an unexistent cid
        for circuitimpact in notification_data["circuitimpacts"]:
            circuitimpact["cid"] = ""

        with patch(
            "nautobot_circuit_maintenance.handle_notifications.handler.get_notifications"
        ) as mock_get_notifications:
            test_notification = generate_email_notification(notification_data, self.source)
            mock_get_notifications.return_value = [test_notification]
            self.job.run(commit=True)
            # Running it again with another notification but for same maintenance wit the same unexistent circuit
            test_notification = generate_email_notification(notification_data, self.source)
            test_notification.subject = "another subject"
            mock_get_notifications.return_value = [test_notification]
            self.job.run(commit=True)

        self.assertEqual(1, len(CircuitMaintenance.objects.all()))
        self.assertEqual(0, len(CircuitImpact.objects.all()))
        self.assertEqual(1, len(Note.objects.all()))

    def test_create_circuit_maintenance_duplicated_circuit_id(self):
        """Test create_circuit_maintenance."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source)
        provider = Provider.objects.get(slug=test_notification.provider_type)
        RawNotification.objects.get_or_create(
            subject=test_notification.subject[:MAX_NOTIFICATION_SUBJECT_LENGTH],
            provider=provider,
            raw=test_notification.raw_payload,
            sender=test_notification.sender,
            source=self.notification_source,
            stamp=datetime.now(timezone.utc),
        )
        parser_provider = init_provider(provider_type=test_notification.provider_type)
        data_to_process = NotificationData.init_from_email_bytes(test_notification.raw_payload)
        parsed_maintenance = parser_provider.get_maintenances(data_to_process)[0]
        # Duplicating the circuit ID
        parsed_maintenance.circuits[1].circuit_id = parsed_maintenance.circuits[0].circuit_id
        create_circuit_maintenance(
            self.job,
            test_notification,
            f"{provider.slug}-{parsed_maintenance.maintenance_id}",
            parsed_maintenance,
            provider,
        )
        self.assertEqual(1, len(CircuitMaintenance.objects.all()))
        self.assertEqual(1, len(CircuitImpact.objects.all()))
        self.assertEqual(0, len(Note.objects.all()))
