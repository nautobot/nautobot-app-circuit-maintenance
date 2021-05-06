"""Tests for Handle Notifications methods."""
from unittest import mock
from django.test import TestCase
from jinja2 import Template

from nautobot.circuits.models import Circuit, Provider
from circuit_maintenance_parser import MaintenanceNotification

from nautobot_circuit_maintenance.handle_notifications.handler import HandleCircuitMaintenanceNotifications

from nautobot_circuit_maintenance.models import (
    CircuitMaintenance,
    CircuitImpact,
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
        source="gmail",
        raw=template.render(obj=notification_data),
        provider_type=notification_data["provider"],
    )


class TestHandleNotificationsJob(TestCase):
    """Test case for all the related methods in Handle Notifications."""

    fixtures = ["handle_notifications_job.yaml"]

    def test_run_simple(self):
        """Test the simple execution to create a Circuit Maintenance."""

        provider = Provider.objects.get(slug="ntt")

        notifications_data = {
            "provider": provider.slug,
            "account": f"ACC-{provider.slug.upper()}",
            "name": f"MNT-{provider.slug.upper()}",
            "status": "CONFIRMED",
            "circuitimpacts": [],
        }

        sample_circuits = Circuit.objects.filter(provider=provider)
        for circuit in sample_circuits:
            notifications_data["circuitimpacts"].append({"cid": circuit.cid, "impact": "NO-IMPACT"})

        test_notification = generate_raw_notification(notifications_data)

        job = HandleCircuitMaintenanceNotifications()
        job.job_result = mock.Mock()
        job.job_result.log = mock.Mock()

        with mock.patch(
            "nautobot_circuit_maintenance.handle_notifications.handler.get_notifications_from_email"
        ) as mock_get_notifications_from_email:
            mock_get_notifications_from_email.return_value = [test_notification]
            processed_notifications = job.run(commit=True)
            mock_get_notifications_from_email.assert_called_once()
            self.assertEqual(1, len(processed_notifications))
            self.assertEqual(1, len(RawNotification.objects.all()))
            self.assertEqual(1, len(ParsedNotification.objects.all()))
            self.assertEqual(1, len(CircuitMaintenance.objects.all()))
            self.assertEqual(2, len(CircuitImpact.objects.all()))
            self.assertEqual(0, len(Note.objects.all()))
