"""Test email_helpers utils."""
from unittest.mock import Mock, patch

from django.test import TestCase
from parameterized import parameterized
from pydantic.error_wrappers import ValidationError  # pylint: disable=no-name-in-module
from nautobot.circuits.models import Provider

from nautobot_circuit_maintenance.models import NotificationSource

from nautobot_circuit_maintenance.handle_notifications.email_helper import IMAP, get_notifications_from_email
from .test_handler import get_base_notification_data, generate_raw_notification


class TestEmailHelper(TestCase):
    """Test case for all the related methods in Email Helper."""

    fixtures = ["handle_notifications_job.yaml"]

    logger = Mock()
    logger.log_info = Mock()
    logger.log_warning = Mock()

    def test_get_notifications_from_email_without_providers(self):
        """Test get_notifications_from_email when there are no Providers defined."""
        email_settings = NotificationSource.objects.all().first()
        email_settings.providers.set([])

        res = get_notifications_from_email(self.logger, NotificationSource.objects.all())
        self.assertEqual([], res)
        self.logger.log_warning.assert_called_with(message="Skipping this email account no providers were defined.")

    @patch("nautobot_circuit_maintenance.handle_notifications.email_helper.IMAP.receive_emails")
    def test_get_notifications_from_email_without_notifications(self, mock_receive_emails):
        """Test get_notifications_from_email with provider without email."""
        mock_receive_emails.return_value = []
        original_provider = Provider.objects.all().first()
        new_provider = Provider.objects.create(name="something", slug="something")
        email_settings = NotificationSource.objects.all().first()
        email_settings.providers.add(new_provider)

        res = get_notifications_from_email(self.logger, NotificationSource.objects.all())
        self.assertEqual([], res)

        self.logger.log_warning.assert_called_with(
            message=f"Skipping {new_provider.name} because these providers has no email configured."
        )
        self.logger.log_info.assert_called_with(
            message=f"No notifications received for {original_provider} since always from {email_settings.source_id}"
        )

    @patch("nautobot_circuit_maintenance.handle_notifications.email_helper.IMAP.receive_emails")
    def test_get_notifications_from_email(self, mock_receive_emails):
        """Test get_notifications_from_email with provider without email."""

        notification_data = get_base_notification_data()
        notification = generate_raw_notification(notification_data)

        mock_receive_emails.return_value = [notification]

        res = get_notifications_from_email(self.logger, NotificationSource.objects.all())

        self.assertEqual(1, len(res))
        self.logger.log_warning.assert_not_called()

    @patch("nautobot_circuit_maintenance.handle_notifications.email_helper.IMAP.receive_emails")
    def test_get_notifications_from_email_multiple(self, mock_receive_emails):
        """Test get_notifications_from_email with provider without email."""

        notification_data = get_base_notification_data()
        notification = generate_raw_notification(notification_data)

        mock_receive_emails.return_value = [notification, notification]

        res = get_notifications_from_email(self.logger, NotificationSource.objects.all())

        self.assertEqual(2, len(res))
        self.logger.log_warning.assert_not_called()

    @parameterized.expand(
        [
            ["service_1", "user_1", "password_1", "imap_url_1", False],
            ["service_1", None, "password_1", "imap_url_1", True],
            ["service_1", "user_1", None, "imap_url_1", True],
            ["service_1", "user_1", "password_1", None, True],
        ]  # pylint: disable=too-many-arguments
    )
    def test_imap_init(self, service, user, password, imap_url, exception):
        """Test IMAP class init."""
        if exception:
            with self.assertRaises(ValidationError):
                IMAP(service=service, user=user, password=password, imap_url=imap_url)
        else:
            IMAP(service=service, user=user, password=password, imap_url=imap_url)
