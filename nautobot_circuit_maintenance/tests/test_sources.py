"""Test sourcess utils."""
from unittest.mock import Mock, patch
from django.conf import settings
from django.test import TestCase
from parameterized import parameterized
from pydantic.error_wrappers import ValidationError  # pylint: disable=no-name-in-module
from nautobot.circuits.models import Provider

from nautobot_circuit_maintenance.models import NotificationSource

from nautobot_circuit_maintenance.handle_notifications.sources import Source, IMAP, get_notifications
from .test_handler import get_base_notification_data, generate_raw_notification


SOURCE_1 = {
    "alias": "example",
    "account": "me@example.com",
    "secret": "supersecret",
    "url": "imap://example.com",
}


class TestSources(TestCase):
    """Test case for all the related methods in Email Helper."""

    fixtures = ["handle_notifications_job.yaml"]

    logger = Mock()
    logger.log_info = Mock()
    logger.log_warning = Mock()

    def setUp(self):
        """Prepare data for tests."""

        settings.PLUGINS_CONFIG = {"nautobot_circuit_maintenance": {"notification_sources": [SOURCE_1]}}
        # Deleting other NotificationSource to define a reliable state.
        NotificationSource.objects.exclude(alias=SOURCE_1["alias"]).delete()

    def test_source_factory(self):
        """Validate Factory pattern for Source class."""
        source_instance = Source.init(alias=SOURCE_1["alias"])
        self.assertIsInstance(source_instance, IMAP)
        self.assertEqual(source_instance.alias, SOURCE_1["alias"])
        self.assertEqual(source_instance.url, SOURCE_1["url"])
        self.assertEqual(source_instance.user, SOURCE_1["account"])
        self.assertEqual(source_instance.password, SOURCE_1["secret"])
        self.assertEqual(source_instance.imap_server, "example.com")
        self.assertEqual(source_instance.imap_port, 993)

    def test_get_notifications_without_providers(self):
        """Test get_notifications when there are no Providers defined."""
        email_settings = NotificationSource.objects.all().first()
        email_settings.providers.set([])

        res = get_notifications(self.logger, NotificationSource.objects.all())
        self.assertEqual([], res)
        self.logger.log_warning.assert_called_with(message="Skipping this email account no providers were defined.")

    @patch("nautobot_circuit_maintenance.handle_notifications.sources.IMAP.receive_notifications")
    def test_get_notifications_without_notifications(self, mock_receive_notifications):
        """Test get_notifications with provider without email."""
        mock_receive_notifications.return_value = []
        original_provider = Provider.objects.all().first()
        new_provider = Provider.objects.create(name="something", slug="something")
        email_settings = NotificationSource.objects.all().first()
        email_settings.providers.add(new_provider)

        res = get_notifications(self.logger, NotificationSource.objects.all())
        self.assertEqual([], res)

        self.logger.log_warning.assert_called_with(
            message=f"Skipping {new_provider.name} because these providers has no email configured."
        )
        self.logger.log_info.assert_called_with(
            message=f"No notifications received for {original_provider} since always from {email_settings.alias}"
        )

    @patch("nautobot_circuit_maintenance.handle_notifications.sources.IMAP.receive_notifications")
    def test_get_notifications(self, mock_receive_notifications):
        """Test get_notifications with provider without email."""
        notification_data = get_base_notification_data()
        notification = generate_raw_notification(notification_data)

        mock_receive_notifications.return_value = [notification]

        res = get_notifications(self.logger, NotificationSource.objects.all())

        self.assertEqual(1, len(res))
        self.logger.log_warning.assert_not_called()

    @patch("nautobot_circuit_maintenance.handle_notifications.sources.IMAP.receive_notifications")
    def test_get_notifications_multiple(self, mock_receive_notifications):
        """Test get_notifications with provider without email."""

        notification_data = get_base_notification_data()
        notification = generate_raw_notification(notification_data)

        mock_receive_notifications.return_value = [notification, notification]

        res = get_notifications(self.logger, NotificationSource.objects.all())

        self.assertEqual(2, len(res))
        self.logger.log_warning.assert_not_called()

    @parameterized.expand(
        [
            ["alias_1", "url1", "user_1", "password_1", "imap_server", 993, False],
            ["alias_1", "url1", None, "password_1", "imap_server", 993, True],
            ["alias_1", "url1", "user_1", None, "imap_server", 993, True],
            ["alias_1", "url1", "user_1", "password_1", None, 993, True],
            ["alias_1", "url1", "user_1", "password_1", "imap_server", None, False],
        ]  # pylint: disable=too-many-arguments
    )
    def test_imap_init(self, alias, url, user, password, imap_server, imap_port, exception):
        """Test IMAP class init."""
        kwargs = {}
        if alias:
            kwargs["alias"] = alias
        if url:
            kwargs["url"] = url
        if user:
            kwargs["user"] = user
        if password:
            kwargs["password"] = password
        if imap_server:
            kwargs["imap_server"] = imap_server
        if imap_port:
            kwargs["imap_port"] = imap_port

        if exception:
            with self.assertRaises(ValidationError):
                IMAP(**kwargs)
        else:
            IMAP(**kwargs)
