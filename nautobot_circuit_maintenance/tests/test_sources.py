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
    "name": "example",
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
        settings.PLUGINS_CONFIG = {"nautobot_circuit_maintenance": {"notification_sources": [SOURCE_1.copy()]}}
        # Deleting other NotificationSource to define a reliable state.
        NotificationSource.objects.exclude(name=SOURCE_1["name"]).delete()

    def test_source_factory(self):
        """Validate Factory pattern for Source class."""
        source_instance = Source.init(name=SOURCE_1["name"])
        self.assertIsInstance(source_instance, IMAP)
        self.assertEqual(source_instance.name, SOURCE_1["name"])
        self.assertEqual(source_instance.url, SOURCE_1["url"])
        self.assertEqual(source_instance.user, SOURCE_1["account"])
        self.assertEqual(source_instance.password, SOURCE_1["secret"])
        self.assertEqual(source_instance.imap_server, "example.com")
        self.assertEqual(source_instance.imap_port, 993)

    def test_source_factory_nonexistent_name(self):
        """Validate Factory pattern for non existent name."""
        non_existent_name = "abc"
        with self.assertRaisesMessage(ValueError, f"Name {non_existent_name} not found in PLUGINS_CONFIG."):
            Source.init(name=non_existent_name)

    def test_source_factory_nonexistent_url(self):
        """Validate Factory pattern for non existent url."""
        del settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"][0]["url"]
        with self.assertRaisesMessage(ValueError, f"URL for {SOURCE_1['name']} not found in PLUGINS_CONFIG"):
            Source.init(name=SOURCE_1["name"])

    def test_source_factory_url_scheme_not_supported(self):
        """Validate Factory pattern for non existent url scheme."""
        settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"][0]["url"] = "ftp://example.com"
        with self.assertRaisesMessage(ValueError, "Scheme ftp not supported as Notification Source (only IMAP)."):
            Source.init(name=SOURCE_1["name"])

    def test_source_factory_url_malformed(self):
        """Validate Factory pattern for malformed url."""
        settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"][0]["url"] = "wrong url"
        with self.assertRaisesMessage(ValueError, "Scheme  not supported as Notification Source (only IMAP)"):
            Source.init(name=SOURCE_1["name"])

    def test_source_factory_imap_no_account(self):
        """Validate Factory pattern IMAP without account settings."""
        del settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"][0]["account"]
        with self.assertRaises(ValidationError):
            Source.init(name=SOURCE_1["name"])

    def test_source_factory_imap_no_secret(self):
        """Validate Factory pattern IMAP without secret settings."""
        del settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"][0]["secret"]
        with self.assertRaises(ValidationError):
            Source.init(name=SOURCE_1["name"])

    def test_get_notifications_without_providers(self):
        """Test get_notifications when there are no Providers defined."""
        notification_source = NotificationSource.objects.all().first()
        notification_source.providers.set([])

        res = get_notifications(self.logger, NotificationSource.objects.all())
        self.assertEqual([], res)
        self.logger.log_warning.assert_called_with(message="Skipping this email account no providers were defined.")

    @patch("nautobot_circuit_maintenance.handle_notifications.sources.IMAP.receive_notifications")
    def test_get_notifications_without_notifications(self, mock_receive_notifications):
        """Test get_notifications with provider without email."""
        mock_receive_notifications.return_value = []
        original_provider = Provider.objects.all().first()
        new_provider = Provider.objects.create(name="something", slug="something")
        notification_source = NotificationSource.objects.all().first()
        notification_source.providers.add(new_provider)

        res = get_notifications(self.logger, NotificationSource.objects.all())
        self.assertEqual([], res)

        self.logger.log_warning.assert_called_with(
            message=f"Skipping {new_provider.name} because these providers has no email configured."
        )
        self.logger.log_info.assert_called_with(
            message=f"No notifications received for {original_provider} since always from {notification_source.name}"
        )

    def test_get_notifications_no_imap_account(self):
        """Test get_notifications without IMAP account."""
        del settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"][0]["account"]
        get_notifications(self.logger, NotificationSource.objects.all())

        self.logger.log_warning.assert_called_with(
            message=f"Notification Source {SOURCE_1['name']} is not matching class expectations: 1 validation error for IMAP\nuser\n  none is not an allowed value (type=type_error.none.not_allowed)"
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
            ["name_1", "url1", "user_1", "password_1", "imap_server", 993, False],
            ["name_1", "url1", None, "password_1", "imap_server", 993, True],
            ["name_1", "url1", "user_1", None, "imap_server", 993, True],
            ["name_1", "url1", "user_1", "password_1", None, 993, True],
            ["name_1", "url1", "user_1", "password_1", "imap_server", None, False],
        ]  # pylint: disable=too-many-arguments
    )
    def test_imap_init(self, name, url, user, password, imap_server, imap_port, exception):
        """Test IMAP class init."""
        kwargs = {}
        if name:
            kwargs["name"] = name
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
