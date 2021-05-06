from unittest import mock
from django.test import TestCase
from jinja2 import Template

from nautobot.circuits.models import Circuit, Provider
from circuit_maintenance_parser import MaintenanceNotification

from nautobot_circuit_maintenance.jobs.handle_notifications import HandleCircuitMaintenanceNotifications

from nautobot_circuit_maintenance.models import CircuitMaintenance, CircuitImpact, EmailSettings


def generate_notification(provider_slug="ntt"):
    """Generate raw notification text for a provider."""
    raw_notifications_template = """
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
    provider = Provider.objects.get(slug=provider_slug)

    notifications_data = {
        "provider": provider,
        "account": f"ACC-{provider.slug.upper()}",
        "name": f"MNT-{provider.slug.upper()}",
        "status": "SCHEDULED",
        "circuitimpacts": [],
    }

    sample_circuits = Circuit.objects.filter(provider=provider)
    for circuit in sample_circuits:
        notifications_data["circuitimpacts"].append(
            {
                "cid": circuit.cid,
                "impact": "NO-IMPACT",
            }
        )

    template = Template(raw_notifications_template)
    return MaintenanceNotification(
        raw=template.render(obj=notifications_data),
        provider_type=provider_slug,
    )


class TestHandleNotificationsJob(TestCase):
    """"""

    fixtures = ["handle_notifications_job.yaml"]

    # @mock.patch.object(email_helper, "get_notifications_from_email")
    def test_run(self):

        test_notification = generate_notification()
        print(test_notification)

        job = HandleCircuitMaintenanceNotifications()
        job.job_result = mock.Mock()
        job.job_result.log = mock.Mock()

        with mock.patch(
            "nautobot_circuit_maintenance.jobs.handle_notifications.get_notifications_from_email"
        ) as mock_get_notifications_from_email:
            # mock_get_notifications_from_email.return_value = [test_notification]
            mock_get_notifications_from_email.side_effect = [test_notification]
            processed_notifications = job.run(commit=True)
            print(job.job_result.log.call_args_list)
            mock_get_notifications_from_email.assert_called_once()
            self.assertEqual(1, len(processed_notifications))
            self.assertEqual(1, len(CircuitMaintenance.objects.all()))
            self.assertEqual(2, len(CircuitImpact.objects.all()))
