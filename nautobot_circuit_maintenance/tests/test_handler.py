"""Tests for Handle Notifications methods."""
from unittest.mock import Mock, patch
from email.message import EmailMessage
from email.utils import formatdate
from django.test import TestCase
from jinja2 import Template
from nautobot.circuits.models import Circuit, Provider
from circuit_maintenance_parser import init_provider, NotificationData

from nautobot_circuit_maintenance.handle_notifications.handler import (
    HandleCircuitMaintenanceNotifications,
    process_raw_notification,
    create_circuit_maintenance,
    update_circuit_maintenance,
    get_maintenances_from_notification,
)

from nautobot_circuit_maintenance.models import (
    CircuitMaintenance,
    CircuitImpact,
    NotificationSource,
    Note,
    RawNotification,
    ParsedNotification,
)
from nautobot_circuit_maintenance.handle_notifications.sources import MaintenanceNotification


def generate_email_notification(notification_data, source):
    """Generate email notification text for a provider."""
    raw_notification_template = """
BEGIN:VCALENDAR
PRODID:Data::ICal 0.16
VERSION:2.0
BEGIN:VEVENT
DESCRIPTION:{{ obj.provider }} URGENT Maintenance Notification: {{ obj.status }} [{{ obj.name }}] Please refer to the email notification for more details regarding maintenance or outage reason and impact.
DTEND:20210808T071300Z
DTSTAMP:20210806T224928Z
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
    email_message["Date"] = formatdate()
    email_message["Subject"] = "Test subject"
    email_message["Content-Type"] = "text/calendar"
    email_message.set_payload(template.render(obj=notification_data).encode("utf-8"))

    return MaintenanceNotification(
        subject="Test subject",
        sender="sender@example.com",
        source=source,
        raw_payload=email_message.as_bytes(),
        provider_type=notification_data["provider"],
        date="Mon, 1 Feb 2021 09:33:34 +0000",
    )


def get_base_notification_data(provider_slug="ntt"):
    """Provides a dictionary of notification data to build notifications."""
    provider = Provider.objects.get(slug=provider_slug)

    notification_data = {
        "provider": provider.slug,
        "account": f"ACC-{provider.slug.upper()}",
        "name": f"MNT-{provider.slug.upper()}",
        "status": "CONFIRMED",
        "circuitimpacts": [],
    }

    sample_circuits = Circuit.objects.filter(provider=provider)
    for circuit in sample_circuits:
        notification_data["circuitimpacts"].append({"cid": circuit.cid, "impact": "NO-IMPACT"})

    return notification_data


class TestHandleNotificationsJob(TestCase):
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
        self.source = NotificationSource.objects.create(name="whatever 1", slug="whatever-1")

    def test_run_simple(self):
        """Test the simple execution to create a Circuit Maintenance."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source.name)

        with patch(
            "nautobot_circuit_maintenance.handle_notifications.handler.get_notifications"
        ) as mock_get_notifications:
            mock_get_notifications.return_value = [test_notification]
            processed_notifications = self.job.run(commit=True)

            mock_get_notifications.assert_called_once()
            self.assertEqual(1, len(processed_notifications))
            self.assertEqual(1, len(RawNotification.objects.all()))
            self.assertEqual(1, len(ParsedNotification.objects.all()))
            self.assertEqual(1, len(CircuitMaintenance.objects.all()))
            self.assertEqual(2, len(CircuitImpact.objects.all()))
            self.assertEqual(0, len(Note.objects.all()))
            self.job.log_debug.assert_called_with("1 notifications processed.")

    def test_run_nonexistent_circuit(self):
        """Test when a Notification contains a nonexistent circuit."""
        notification_data = get_base_notification_data()
        fake_cid = "nonexistent circuit"
        notification_data["circuitimpacts"].append({"cid": fake_cid, "impact": "NO-IMPACT"})
        test_notification = generate_email_notification(notification_data, self.source.name)

        with patch(
            "nautobot_circuit_maintenance.handle_notifications.handler.get_notifications"
        ) as mock_get_notifications:
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
            self.job.log_debug.assert_called_with("1 notifications processed.")

    def test_run_nonotifications(self):
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

    def test_run_nonnotificationsource(self):
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
        test_notification = generate_email_notification(notification_data, self.source.name)

        with patch(
            "nautobot_circuit_maintenance.handle_notifications.handler.get_notifications"
        ) as mock_get_notifications:
            mock_get_notifications.return_value = [test_notification]
            processed_notifications = self.job.run(commit=True)

            mock_get_notifications.assert_called_once()
            self.assertEqual(1, len(processed_notifications))
            self.assertEqual(1, len(RawNotification.objects.all()))
            self.assertEqual(0, len(ParsedNotification.objects.all()))
            self.assertEqual(0, len(CircuitMaintenance.objects.all()))
            self.assertEqual(0, len(CircuitImpact.objects.all()))
            self.assertEqual(0, len(Note.objects.all()))
            self.job.log_warning.assert_called()
            self.job.log_debug.assert_called_with("1 notifications processed.")

    def test_process_raw_notification_no_provider_in_parser(self):
        """Test process_raw_notification with non existant Proivder in the parser library."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source.name)
        test_notification.provider_type = "abc"
        res = process_raw_notification(self.job, test_notification)
        self.assertNotEqual(res, None)
        self.job.log_warning.assert_called_with(
            message=f"Notification Parser not found for {test_notification.provider_type}"
        )

    def test_process_raw_notification_no_provider_in_plugin(self):
        """Test process_raw_notification with non existant provider in the Plugin."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source.name)
        test_notification.provider_type = "telstra"
        res = process_raw_notification(self.job, test_notification)
        self.assertEqual(res, None)
        self.job.log_warning.assert_called_with(
            message=f"Raw notification not created because is referencing to a provider not existent: {test_notification.provider_type}"
        )

    def test_process_raw_notification(self):
        """Test process_raw_notification."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source.name)
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
        test_notification = generate_email_notification(notification_data, self.source.name)

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
        test_notification = generate_email_notification(notification_data, self.source.name)
        res = process_raw_notification(self.job, test_notification)

        raw_notification = RawNotification.objects.get(pk=res)
        self.assertEqual(raw_notification.pk, res)
        self.assertEqual(raw_notification.parsed, False)
        self.assertEqual(0, len(ParsedNotification.objects.all()))
        self.job.log_success.assert_any_call(raw_notification, message="Raw notification created.")
        self.job.log_warning.assert_called()

    def test_get_maintenances_from_notification(self):
        """Test get_maintenances_from_notification."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source.name)
        provider = Provider.objects.get(slug=test_notification.provider_type)
        parser_maintenances = get_maintenances_from_notification(self.job, test_notification, provider)
        self.assertEqual(1, len(parser_maintenances))

    def test_get_maintenances_from_notification_wrong_data(self):
        """Test get_maintenances_from_notification."""
        notification_data = get_base_notification_data()
        notification_data["status"] = "Non valid status"
        test_notification = generate_email_notification(notification_data, self.source.name)
        provider = Provider.objects.get(slug=test_notification.provider_type)
        parser_maintenances = get_maintenances_from_notification(self.job, test_notification, provider)
        self.assertIsNone(parser_maintenances)
        self.job.log_failure.assert_called()

    def test_get_maintenances_from_notification_non_existent_provider_in_parser(self):
        """Test get_maintenances_from_notification."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source.name)
        provider = Provider.objects.get(slug=test_notification.provider_type)
        provider.cf["provider_parser_circuit_maintenances"] = "unkown_provider_in_parser"
        parser_maintenances = get_maintenances_from_notification(self.job, test_notification, provider)
        self.assertIsNone(parser_maintenances)
        self.job.log_warning.assert_any_call(message=f"Notification Parser not found for {provider.slug}")

    def test_create_circuit_maintenance(self):
        """Test create_circuit_maintenance."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source.name)
        provider = Provider.objects.get(slug=test_notification.provider_type)
        raw_entry, _ = RawNotification.objects.get_or_create(
            subject=test_notification.subject,
            provider=provider,
            raw=test_notification.raw_payload,
            sender=test_notification.sender,
            source=self.source,
        )
        parser_provider = init_provider(provider_type=test_notification.provider_type)
        data_to_process = NotificationData.init_from_email_bytes(test_notification.raw_payload)
        parsed_maintenance = parser_provider.get_maintenances(data_to_process)[0]
        create_circuit_maintenance(self.job, raw_entry.id, parsed_maintenance, provider)
        self.assertEqual(1, len(CircuitMaintenance.objects.all()))
        self.assertEqual(2, len(CircuitImpact.objects.all()))
        self.assertEqual(0, len(Note.objects.all()))

    def test_create_circuit_maintenance_no_circuits(self):
        """Test create_circuit_maintenance without existent circuits."""
        notification_data = get_base_notification_data()
        notification_data["circuitimpacts"] = [{"cid": "nonexistent", "impact": "NO-IMPACT"}]
        test_notification = generate_email_notification(notification_data, self.source.name)
        provider = Provider.objects.get(slug=test_notification.provider_type)
        raw_entry, _ = RawNotification.objects.get_or_create(
            subject=test_notification.subject,
            provider=provider,
            raw=test_notification.raw_payload,
            sender=test_notification.sender,
            source=self.source,
        )
        parser_provider = init_provider(provider_type=test_notification.provider_type)
        data_to_process = NotificationData.init_from_email_bytes(test_notification.raw_payload)
        parsed_maintenance = parser_provider.get_maintenances(data_to_process)[0]
        create_circuit_maintenance(self.job, raw_entry.id, parsed_maintenance, provider)
        self.assertEqual(1, len(CircuitMaintenance.objects.all()))
        self.assertEqual(0, len(CircuitImpact.objects.all()))
        self.assertEqual(1, len(Note.objects.all()))

    def test_update_circuit_maintenance(self):
        """Test update_circuit_maintenance."""
        notification_data = get_base_notification_data()
        test_notification = generate_email_notification(notification_data, self.source.name)
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
        test_notification = generate_email_notification(notification_data, self.source.name)
        parser_provider = init_provider(provider_type=test_notification.provider_type)
        data_to_process = NotificationData.init_from_email_bytes(test_notification.raw_payload)
        parsed_maintenance = parser_provider.get_maintenances(data_to_process)[0]
        maintenance_id = f"{provider.slug}-{parsed_maintenance.maintenance_id}"
        circuit_maintenance_entry = CircuitMaintenance.objects.get(name=maintenance_id)
        update_circuit_maintenance(self.job, circuit_maintenance_entry, maintenance_id, parsed_maintenance, provider)
        self.assertEqual(1, len(CircuitMaintenance.objects.all()))
        self.assertEqual(1, len(CircuitImpact.objects.all()))
        self.assertEqual(1, len(Note.objects.all()))
        circuit_maintenance_entry = CircuitMaintenance.objects.get(name=maintenance_id)
        self.assertEqual(notification_data["status"], circuit_maintenance_entry.status)
        circuit_impact_entry = CircuitImpact.objects.get(circuit__cid=circuit_to_update["cid"])
        self.assertEqual(circuit_to_update["impact"], circuit_impact_entry.impact)

    def test_update_circuit_maintenance_unordered_notifications(self):
        """Test update_circuit_maintenance with unordered notifications."""
        notification_data = get_base_notification_data()
        test_notification_older = generate_email_notification(notification_data, self.source.name)

        notification_data["status"] = "COMPLETED"
        test_notification_newer = generate_email_notification(notification_data, self.source.name)
        test_notification_newer.date = "Mon, 2 Feb 2021 09:33:34 +0000"

        provider = Provider.objects.get(slug=test_notification_older.provider_type)
        with patch(
            "nautobot_circuit_maintenance.handle_notifications.handler.get_notifications"
        ) as mock_get_notifications:
            # We simulate that the newer notifications are retrieved first, so processed first
            mock_get_notifications.return_value = [test_notification_newer, test_notification_older]
            self.job.run(commit=True)

        # Verify that both notifications where related to same CircuitMaintenance
        self.assertEqual(1, len(CircuitMaintenance.objects.all()))

        maintenance_id = f"{provider.slug}-{notification_data['name']}"
        circuit_maintenance_entry = CircuitMaintenance.objects.get(name=maintenance_id)
        # Verify that the final status of the CircuitMaintenance depends on the newest notification
        self.assertEqual(circuit_maintenance_entry.status, "COMPLETED")
        # Verify that both parsed notifications are linked to the CircuitMaintenance for future reference
        self.assertEqual(len(circuit_maintenance_entry.parsednotification_set.all()), 2)
