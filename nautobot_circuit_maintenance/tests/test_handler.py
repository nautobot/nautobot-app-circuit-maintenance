"""Tests for Handle Notifications methods."""
from unittest.mock import Mock, patch
from django.test import TestCase
from jinja2 import Template

from nautobot.circuits.models import Circuit, Provider
from circuit_maintenance_parser import MaintenanceNotification, init_parser

from nautobot_circuit_maintenance.handle_notifications.handler import (
    HandleCircuitMaintenanceNotifications,
    process_raw_notification,
    create_circuit_maintenance,
    update_circuit_maintenance,
)

from nautobot_circuit_maintenance.models import (
    CircuitMaintenance,
    CircuitImpact,
    NotificationSource,
    Note,
    RawNotification,
    ParsedNotification,
)


def generate_raw_notification(notification_data):
    """Generate raw notification text for a provider."""
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
    return MaintenanceNotification(
        subject="Test subject",
        sender="sender@example.com",
        source="imap",
        raw=template.render(obj=notification_data),
        provider_type=notification_data["provider"],
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
    job._job_result = Mock()  # pylint: disable=protected-access
    job.log_debug = Mock()
    job.log_info = Mock()
    job.log_warning = Mock()
    job.log_failure = Mock()
    job.log_success = Mock()

    def test_run_simple(self):
        """Test the simple execution to create a Circuit Maintenance."""
        notification_data = get_base_notification_data()
        test_notification = generate_raw_notification(notification_data)

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
        test_notification = generate_raw_notification(notification_data)

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
        test_notification = generate_raw_notification(notification_data)

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

    def test_process_raw_notification_no_parser(self):
        """Test process_raw_notification with non existant parser."""
        notification_data = get_base_notification_data()
        test_notification = generate_raw_notification(notification_data)
        test_notification.provider_type = "unknown"
        res = process_raw_notification(self.job, test_notification)
        self.assertEqual(res, None)
        self.job.log_warning.assert_called_with(
            message=f"Notification Parser not found for {test_notification.provider_type}"
        )

    def test_process_raw_notification_no_provider_type(self):
        """Test process_raw_notification with non existant provider_type."""
        notification_data = get_base_notification_data()
        test_notification = generate_raw_notification(notification_data)
        test_notification.provider_type = "ICal"
        res = process_raw_notification(self.job, test_notification)
        self.assertEqual(res, None)
        self.job.log_warning.assert_called_with(
            message=f"Raw notification not created because is referencing to a provider not existent {test_notification.provider_type}"
        )

    def test_process_raw_notification(self):
        """Test process_raw_notification."""
        notification_data = get_base_notification_data()
        test_notification = generate_raw_notification(notification_data)
        res = process_raw_notification(self.job, test_notification)

        raw_notification = RawNotification.objects.get(pk=res)
        self.assertEqual(raw_notification.pk, res)
        self.assertEqual(raw_notification.parsed, True)
        self.assertEqual(1, len(ParsedNotification.objects.all()))
        self.job.log_success.assert_any_call(raw_notification, message="Raw notification created.")

    def test_process_raw_notification_parser_issue(self):
        """Test process_raw_notification with parsing issues"""
        notification_data = get_base_notification_data()
        notification_data["status"] = "Non valid status"
        test_notification = generate_raw_notification(notification_data)
        res = process_raw_notification(self.job, test_notification)

        raw_notification = RawNotification.objects.get(pk=res)
        self.assertEqual(raw_notification.pk, res)
        self.assertEqual(raw_notification.parsed, False)
        self.assertEqual(0, len(ParsedNotification.objects.all()))
        self.job.log_success.assert_any_call(raw_notification, message="Raw notification created.")
        self.job.log_warning.assert_called()

    def test_create_circuit_maintenance(self):
        """Test create_circuit_maintenance."""
        notification_data = get_base_notification_data()
        test_notification = generate_raw_notification(notification_data)

        parser = init_parser(**test_notification.__dict__)
        raw_entry, _ = RawNotification.objects.get_or_create(
            subject=parser.subject,
            provider=Provider.objects.get(slug=parser.provider_type),
            raw=parser.raw,
            sender=parser.sender,
            source=parser.source,
        )
        parsed_maintenance = parser.process()[0]
        create_circuit_maintenance(self.job, raw_entry.id, parsed_maintenance)
        self.assertEqual(1, len(CircuitMaintenance.objects.all()))
        self.assertEqual(2, len(CircuitImpact.objects.all()))
        self.assertEqual(0, len(Note.objects.all()))

    def test_create_circuit_maintenance_no_circuits(self):
        """Test create_circuit_maintenance without existent circuits."""
        notification_data = get_base_notification_data()
        notification_data["circuitimpacts"] = [{"cid": "nonexistent", "impact": "NO-IMPACT"}]
        test_notification = generate_raw_notification(notification_data)

        parser = init_parser(**test_notification.__dict__)
        raw_entry, _ = RawNotification.objects.get_or_create(
            subject=parser.subject,
            provider=Provider.objects.get(slug=parser.provider_type),
            raw=parser.raw,
            sender=parser.sender,
            source=parser.source,
        )
        parsed_maintenance = parser.process()[0]
        create_circuit_maintenance(self.job, raw_entry.id, parsed_maintenance)
        self.assertEqual(1, len(CircuitMaintenance.objects.all()))
        self.assertEqual(0, len(CircuitImpact.objects.all()))
        self.assertEqual(1, len(Note.objects.all()))

    def test_update_circuit_maintenance(self):
        """Test update_circuit_maintenance."""
        notification_data = get_base_notification_data()
        test_notification = generate_raw_notification(notification_data)

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

        test_notification = generate_raw_notification(notification_data)
        parser = init_parser(**test_notification.__dict__)

        parsed_maintenance = parser.process()[0]
        maintenance_id = str(parsed_maintenance.maintenance_id)
        circuit_maintenance_entry = CircuitMaintenance.objects.get(name=maintenance_id)
        update_circuit_maintenance(self.job, circuit_maintenance_entry, maintenance_id, parsed_maintenance)
        self.assertEqual(1, len(CircuitMaintenance.objects.all()))
        self.assertEqual(1, len(CircuitImpact.objects.all()))
        self.assertEqual(1, len(Note.objects.all()))
        circuit_maintenance_entry = CircuitMaintenance.objects.get(name=maintenance_id)
        self.assertEqual(notification_data["status"], circuit_maintenance_entry.status)
        circuit_impact_entry = CircuitImpact.objects.get(circuit__cid=circuit_to_update["cid"])
        self.assertEqual(circuit_to_update["impact"], circuit_impact_entry.impact)
