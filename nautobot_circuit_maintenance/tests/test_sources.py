"""Test sourcess utils."""
import base64
from email.message import EmailMessage
import json
import os
from unittest.mock import Mock, patch
import uuid

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from parameterized import parameterized
from pydantic.error_wrappers import ValidationError  # pylint: disable=no-name-in-module

from nautobot.circuits.models import Provider
from nautobot.extras.jobs import Job
from nautobot.extras.models import JobResult, Job as JobModel

from nautobot_circuit_maintenance.models import NotificationSource
from nautobot_circuit_maintenance.handle_notifications.sources import (
    GmailAPIOauth,
    GmailAPI,
    Source,
    IMAP,
    get_notifications,
    GmailAPIServiceAccount,
    EmailSource,
)
from .test_handler import get_base_notification_data, generate_raw_notification


SOURCE_IMAP = {
    "name": "source imap",
    "account": "me@example.com",
    "secret": "supersecret",
    "url": "imap://example.com",
}

SOURCE_GMAIL_API_SERVICE_ACCOUNT = {
    "name": "source gmail api service account",
    "account": "me@example.com",
    "url": "https://accounts.google.com/o/oauth2/auth",
    "credentials_file": "path_to_credentials_service_account.json",
}

SOURCE_GMAIL_API_OAUTH = {
    "name": "source gmail api oauth",
    "account": "me@example.com",
    "url": "https://accounts.google.com/o/oauth2/auth",
    "credentials_file": "path_to_credentials_oauth.json",
}


class TestSource(TestCase):
    """Test case for IMAP Source."""

    fixtures = ["handle_notifications_job.yaml"]

    def setUp(self):
        """Prepare data for tests."""
        settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"] = [
            SOURCE_IMAP.copy(),
            SOURCE_GMAIL_API_SERVICE_ACCOUNT.copy(),
        ]
        # Deleting other NotificationSource to define a reliable state.
        NotificationSource.objects.exclude(
            name__in=[SOURCE_IMAP["name"], SOURCE_GMAIL_API_SERVICE_ACCOUNT["name"]]
        ).delete()

    def test_source_factory_nonexistent_name(self):
        """Validate Factory pattern for non existent name."""
        non_existent_name = "abc"
        with self.assertRaisesMessage(ValueError, f"Name {non_existent_name} not found in PLUGINS_CONFIG."):
            Source.init(name=non_existent_name)

    def test_source_factory_nonexistent_url(self):
        """Validate Factory pattern for non existent url."""
        del settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"][0]["url"]
        with self.assertRaisesMessage(ValueError, f"URL for {SOURCE_IMAP['name']} not found in PLUGINS_CONFIG"):
            Source.init(name=SOURCE_IMAP["name"])

    def test_source_factory_url_scheme_not_supported(self):
        """Validate Factory pattern for non existent url scheme."""
        settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"][0]["url"] = "ftp://example.com"
        with self.assertRaisesMessage(
            ValueError,
            "Scheme ftp not supported as Notification Source (only IMAP or HTTPS to accounts.google.com).",
        ):
            Source.init(name=SOURCE_IMAP["name"])

    def test_source_factory_url_malformed(self):
        """Validate Factory pattern for malformed url."""
        settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"][0]["url"] = "wrong url"
        with self.assertRaisesMessage(
            ValueError,
            "Scheme  not supported as Notification Source (only IMAP or HTTPS to accounts.google.com).",
        ):
            Source.init(name=SOURCE_IMAP["name"])


class TestEmailSource(TestCase):
    """Test case for EmailSource."""

    @parameterized.expand(
        [
            ["user@example.com", "user@example.com"],
            ["<user@example.com>", "user@example.com"],
            ["user <user@example.com>", "user@example.com"],
            ["No-reply via mailing list <mailing-list@example.com>", "mailing-list@example.com"],
        ]  # pylint: disable=too-many-arguments
    )
    def test_extract_email_source(self, email_source, email_source_output):
        """Test for extract_email_source."""
        self.assertEqual(EmailSource.extract_email_source(email_source), email_source_output)

    def test_extract_provider_data_types_no_email(self):
        """Test for extract_provider_data_types when Provider doens't have the email."""
        Provider.objects.create(name="whatever", slug="whatever")
        email_source = "user@example.com"
        self.assertEqual(
            EmailSource.extract_provider_data_types(email_source),
            ("", "", f"Sender email {email_source} is not registered for any circuit provider."),
        )

    def test_extract_provider_data_types_no_provider_parser(self):
        """Test for extract_provider_data_types when Provider doesn't have the email."""
        provider_type = "whatever"
        email_source = "user@example.com"
        provider = Provider.objects.create(name=provider_type, slug=provider_type)
        provider.cf["emails_circuit_maintenances"] = email_source
        provider.save()

        self.assertEqual(
            EmailSource.extract_provider_data_types(email_source),
            (
                "",
                "",
                f"{email_source} is for provider type `{provider_type}`, which is not presently supported",
            ),
        )

    @parameterized.expand(
        [
            ["ntt", {"text/calendar"}, False],
            ["telstra", {"text/html", "text/calendar"}, False],
            ["zayo", {"text/html"}, False],
            ["unknown", "unknown", True],
        ]
    )
    def test_extract_provider_data_types_ok(self, provider_type, data_types, error_message):
        """Test for extract_provider_data_types."""
        email_source = "user@example.com"
        provider = Provider.objects.create(name=provider_type, slug=provider_type)
        provider.cf["emails_circuit_maintenances"] = email_source
        provider.save()

        self.assertEqual(
            EmailSource.extract_provider_data_types(email_source),
            (
                data_types if not error_message else "",
                provider_type if not error_message else "",
                f"{email_source} is for provider type `{provider_type}`, which is not presently supported"
                if error_message
                else "",
            ),
        )

    def test_extract_provider_data_types_multiple_sources(self):
        """Test for extract_provider_data_types with multiple sources defined in the custom field data."""
        email_sources = ["user@example.com", "another-user@example.com"]
        provider = Provider.objects.create(name="ntt", slug="ntt")
        # User-inputted custom field values can be messy - we're testing that here!
        provider.cf["emails_circuit_maintenances"] = " user@example.com, Another-User@example.com, "
        provider.save()

        for email_source in email_sources:
            self.assertEqual(
                EmailSource.extract_provider_data_types(email_source),
                ({"text/calendar"}, "ntt", ""),
            )


class TestIMAPSource(TestCase):
    """Test case for IMAP Source."""

    fixtures = ["source_imap.yaml"]

    logger = Mock()
    logger.log_info = Mock()
    logger.log_warning = Mock()

    def setUp(self):
        """Prepare data for tests."""
        settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"] = [SOURCE_IMAP.copy()]
        # Deleting other NotificationSource to define a reliable state.
        NotificationSource.objects.exclude(name__in=[SOURCE_IMAP["name"]]).delete()
        self.source = NotificationSource.objects.get(name=SOURCE_IMAP["name"])

    def test_source_factory(self):
        """Validate Factory pattern for Source class."""
        source_instance = Source.init(name=SOURCE_IMAP["name"])
        self.assertIsInstance(source_instance, IMAP)
        self.assertEqual(source_instance.name, SOURCE_IMAP["name"])
        self.assertEqual(source_instance.url, SOURCE_IMAP["url"])
        self.assertEqual(source_instance.account, SOURCE_IMAP["account"])
        self.assertEqual(source_instance.password, SOURCE_IMAP["secret"])
        self.assertEqual(source_instance.imap_server, "example.com")
        self.assertEqual(source_instance.imap_port, 993)

    def test_source_factory_imap_no_account(self):
        """Validate Factory pattern IMAP without account settings."""
        del settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"][0]["account"]
        with self.assertRaises(ValidationError):
            Source.init(name=SOURCE_IMAP["name"])

    def test_source_factory_imap_no_secret(self):
        """Validate Factory pattern IMAP without secret settings."""
        del settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"][0]["secret"]
        with self.assertRaises(ValidationError):
            Source.init(name=SOURCE_IMAP["name"])

    def test_get_notifications_without_providers(self):
        """Test get_notifications when there are no Providers defined."""
        notification_source = NotificationSource.objects.get(name=SOURCE_IMAP["name"])
        notification_source.providers.set([])

        res = get_notifications(self.logger, NotificationSource.objects.all())
        self.assertEqual([], res)
        source_name = SOURCE_IMAP["name"]
        self.logger.log_warning.assert_called_with(
            message=f"Skipping source '{source_name}' because no providers were defined."
        )

    @patch("nautobot_circuit_maintenance.handle_notifications.sources.IMAP.receive_notifications")
    def test_get_notifications_without_notifications(self, mock_receive_notifications):
        """Test get_notifications with provider without email in one of the provider and without notifications."""
        mock_receive_notifications.return_value = []
        original_provider = Provider.objects.all().first()
        new_provider = Provider.objects.create(name="something", slug="something")
        notification_source = NotificationSource.objects.all().first()
        notification_source.providers.add(original_provider)
        notification_source.providers.add(new_provider)

        res = get_notifications(self.logger, NotificationSource.objects.all())
        self.assertEqual([], res)

        self.logger.log_warning.assert_called_with(
            message=f"Skipping {new_provider.name} because these providers have no email configured."
        )
        self.logger.log_info.assert_called_with(
            message=f"No notifications received for {original_provider}, {new_provider} since always from {notification_source.name}"
        )

    def test_get_notifications_no_imap_account(self):
        """Test get_notifications without IMAP account."""
        del settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"][0]["account"]
        get_notifications(self.logger, NotificationSource.objects.all())

        self.logger.log_warning.assert_called_with(
            message=f"Notification Source {SOURCE_IMAP['name']} is not matching class expectations: 1 validation error for IMAP\naccount\n  none is not an allowed value (type=type_error.none.not_allowed)"
        )

    @patch("nautobot_circuit_maintenance.handle_notifications.sources.IMAP.receive_notifications")
    def test_get_notifications(self, mock_receive_notifications):
        """Test get_notifications."""
        notification_data = get_base_notification_data()
        notification = generate_raw_notification(notification_data, self.source.name)

        mock_receive_notifications.return_value = [notification]

        res = get_notifications(self.logger, NotificationSource.objects.all())

        self.assertEqual(1, len(res))
        self.logger.log_warning.assert_not_called()

    @patch("nautobot_circuit_maintenance.handle_notifications.sources.IMAP.receive_notifications")
    def test_get_notifications_multiple(self, mock_receive_notifications):
        """Test get_notifications multiple."""
        notification_data = get_base_notification_data()
        notification = generate_raw_notification(notification_data, self.source.name)

        mock_receive_notifications.return_value = [notification, notification]

        res = get_notifications(self.logger, NotificationSource.objects.all())

        self.assertEqual(2, len(res))
        self.logger.log_warning.assert_not_called()

    @patch("nautobot_circuit_maintenance.handle_notifications.sources.IMAP.close_session")
    @patch("nautobot_circuit_maintenance.handle_notifications.sources.IMAP.open_session")
    def test_imap_test_authentication_ok(self, mock_open, mock_close):  # pylint: disable=unused-argument
        source = IMAP(
            name="whatever", url="imap://localhost", account="account", password="pass", imap_server="localhost"
        )
        res, message = source.test_authentication()
        self.assertEqual(res, True)
        self.assertEqual(message, "Test OK")

    @patch("nautobot_circuit_maintenance.handle_notifications.sources.IMAP.open_session")
    def test_imap_test_authentication_ko(self, mock_open):
        mock_open.side_effect = Exception("error message")
        source = IMAP(
            name="whatever", url="imap://localhost", account="account", password="pass", imap_server="localhost"
        )
        res, message = source.test_authentication()
        self.assertEqual(res, False)
        self.assertEqual(message, "error message")

    @parameterized.expand(
        [
            ["name_1", "url1", "user_1", "password_1", "imap_server", 993, False],
            ["name_1", "url1", None, "password_1", "imap_server", 993, True],
            ["name_1", "url1", "user_1", None, "imap_server", 993, True],
            ["name_1", "url1", "user_1", "password_1", None, 993, True],
            ["name_1", "url1", "user_1", "password_1", "imap_server", None, False],
        ]  # pylint: disable=too-many-arguments
    )
    def test_imap_init(self, name, url, account, password, imap_server, imap_port, exception):
        """Test IMAP class init."""
        kwargs = {}
        if name:
            kwargs["name"] = name
        if url:
            kwargs["url"] = url
        if account:
            kwargs["account"] = account
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

    def test_process_email_success(self):
        """Test successful processing of a single email into a MaintenanceNotification."""
        provider = Provider.objects.create(name="zayo", slug="zayo")
        provider.cf["emails_circuit_maintenances"] = "user@example.com"
        provider.save()

        source = IMAP(
            name="whatever", url="imap://localhost", account="account", password="pass", imap_server="localhost"
        )

        job = Job()
        job.job_result = JobResult.objects.create(
            name="dummy", obj_type=ContentType.objects.get_for_model(JobModel), user=None, job_id=uuid.uuid4()
        )

        email_message = EmailMessage()
        email_message["From"] = "User <user@example.com>"
        email_message["Subject"] = "Circuit Maintenance Notification"
        email_message["Content-Type"] = "text/html"
        email_message.set_payload("Some text goes here")

        notification = source.process_email(job, email_message)
        self.assertIsNotNone(notification)
        self.assertEqual(notification.source, source.name)
        self.assertEqual(notification.sender, "User <user@example.com>")
        self.assertEqual(notification.subject, "Circuit Maintenance Notification")
        self.assertEqual(notification.provider_type, "zayo")
        self.assertEqual(list(notification.raw_payloads), ["Some text goes here"])

    def test_process_email_success_alternate_source_header(self):
        """Test successful processing of a single email with a non-standard source header."""
        provider = Provider.objects.create(name="zayo", slug="zayo")
        provider.cf["emails_circuit_maintenances"] = "user@example.com"
        provider.save()

        source = IMAP(
            name="whatever",
            url="imap://localhost",
            account="account",
            password="pass",
            imap_server="localhost",
            source_header="X-Original-Sender",
        )

        job = Job()
        job.job_result = JobResult.objects.create(
            name="dummy", obj_type=ContentType.objects.get_for_model(JobModel), user=None, job_id=uuid.uuid4()
        )

        email_message = EmailMessage()
        email_message["From"] = "Mailing List <mailing-list@example.com>"
        email_message["X-Original-Sender"] = "User <user@example.com>"
        email_message["Subject"] = "Circuit Maintenance Notification"
        email_message["Content-Type"] = "text/html"
        email_message.set_payload("Some text goes here")

        notification = source.process_email(job, email_message)
        self.assertIsNotNone(notification)
        self.assertEqual(notification.source, source.name)
        self.assertEqual(notification.sender, "User <user@example.com>")
        self.assertEqual(notification.subject, "Circuit Maintenance Notification")
        self.assertEqual(notification.provider_type, "zayo")
        self.assertEqual(list(notification.raw_payloads), ["Some text goes here"])


class TestGmailAPISource(TestCase):
    """Test case for GmailAPI Source."""

    fixtures = ["source_gmail_api.yaml"]

    logger = Mock()
    logger.log_info = Mock()
    logger.log_warning = Mock()

    def setUp(self):
        """Prepare data for tests."""
        settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"] = [
            SOURCE_GMAIL_API_SERVICE_ACCOUNT.copy(),
            SOURCE_GMAIL_API_OAUTH.copy(),
        ]
        # Deleting other NotificationSource and Provider to define a reliable state.
        NotificationSource.objects.exclude(name__in=[SOURCE_GMAIL_API_SERVICE_ACCOUNT["name"]]).delete()
        self.source = NotificationSource.objects.get(name=SOURCE_GMAIL_API_SERVICE_ACCOUNT["name"])

        with open(SOURCE_GMAIL_API_SERVICE_ACCOUNT["credentials_file"], "w") as credentials_file:
            json.dump({"type": "service_account"}, credentials_file)

        with open(SOURCE_GMAIL_API_OAUTH["credentials_file"], "w") as credentials_file:
            json.dump({"web": {}}, credentials_file)

    def tearDown(self):
        """Clean up data from tests."""
        os.remove(SOURCE_GMAIL_API_SERVICE_ACCOUNT["credentials_file"])
        os.remove(SOURCE_GMAIL_API_OAUTH["credentials_file"])

    def test_source_factory_service_account(self):
        """Validate Factory pattern for Source class."""
        source_instance = Source.init(name=SOURCE_GMAIL_API_SERVICE_ACCOUNT["name"])
        self.assertIsInstance(source_instance, GmailAPIServiceAccount)
        self.assertEqual(source_instance.name, SOURCE_GMAIL_API_SERVICE_ACCOUNT["name"])
        self.assertEqual(source_instance.url, SOURCE_GMAIL_API_SERVICE_ACCOUNT["url"])
        self.assertEqual(source_instance.account, SOURCE_GMAIL_API_SERVICE_ACCOUNT["account"])
        self.assertEqual(source_instance.credentials_file, SOURCE_GMAIL_API_SERVICE_ACCOUNT["credentials_file"])

    def test_source_factory_oauth(self):
        """Validate Factory pattern for Source class."""
        source_instance = Source.init(name=SOURCE_GMAIL_API_OAUTH["name"])
        self.assertIsInstance(source_instance, GmailAPIOauth)
        self.assertEqual(source_instance.name, SOURCE_GMAIL_API_OAUTH["name"])
        self.assertEqual(source_instance.url, SOURCE_GMAIL_API_OAUTH["url"])
        self.assertEqual(source_instance.account, SOURCE_GMAIL_API_OAUTH["account"])
        self.assertEqual(source_instance.credentials_file, SOURCE_GMAIL_API_OAUTH["credentials_file"])

    def test_source_factory_no_account(self):
        """Validate Factory pattern Gmail API without account settings."""
        del settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"][0]["account"]
        with self.assertRaises(ValidationError):
            Source.init(name=SOURCE_GMAIL_API_SERVICE_ACCOUNT["name"])

    def test_source_factory_no_credentials(self):
        """Validate Factory pattern Gmail API without credentials_file."""
        del settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"][0]["credentials_file"]
        with self.assertRaises(ValueError):
            Source.init(name=SOURCE_GMAIL_API_SERVICE_ACCOUNT["name"])

    def test_source_factory_credentials_file_non_existent(self):
        """Validate Factory pattern Gmail API with credentials_file unexistent."""
        settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"][0]["credentials_file"] = "fake"
        with self.assertRaises(ValueError):
            Source.init(name=SOURCE_GMAIL_API_SERVICE_ACCOUNT["name"])

    def test_get_notifications_without_providers(self):
        """Test get_notifications when there are no Providers defined."""
        notification_source = NotificationSource.objects.get(name=SOURCE_GMAIL_API_SERVICE_ACCOUNT["name"])
        notification_source.providers.set([])

        res = get_notifications(self.logger, NotificationSource.objects.all())
        self.assertEqual([], res)
        source_name = SOURCE_GMAIL_API_SERVICE_ACCOUNT["name"]
        self.logger.log_warning.assert_called_with(
            message=f"Skipping source '{source_name}' because no providers were defined."
        )

    @patch("nautobot_circuit_maintenance.handle_notifications.sources.GmailAPIServiceAccount.receive_notifications")
    def test_get_notifications_without_notifications(self, mock_receive_notifications):
        """Test get_notifications with provider without email in one of the provider and without notifications."""
        mock_receive_notifications.return_value = []
        original_provider = Provider.objects.all().first()
        new_provider = Provider.objects.create(name="something", slug="something")
        notification_source = NotificationSource.objects.all().first()
        notification_source.providers.add(original_provider)
        notification_source.providers.add(new_provider)

        res = get_notifications(self.logger, NotificationSource.objects.all())
        self.assertEqual([], res)

        self.logger.log_warning.assert_called_with(
            message=f"Skipping {new_provider.name} because these providers have no email configured."
        )
        self.logger.log_info.assert_called_with(
            message=f"No notifications received for {original_provider}, {new_provider} since always from {notification_source.name}"
        )

    def test_get_notifications_no_account(self):
        """Test get_notifications without account."""
        del settings.PLUGINS_CONFIG["nautobot_circuit_maintenance"]["notification_sources"][0]["account"]
        get_notifications(self.logger, NotificationSource.objects.all())

        self.logger.log_warning.assert_called_with(
            message=f"Notification Source {SOURCE_GMAIL_API_SERVICE_ACCOUNT['name']} is not matching class expectations: 1 validation error for GmailAPIServiceAccount\naccount\n  none is not an allowed value (type=type_error.none.not_allowed)"
        )

    @patch("nautobot_circuit_maintenance.handle_notifications.sources.GmailAPI.receive_notifications")
    def test_get_notifications(self, mock_receive_notifications):
        """Test get_notifications."""
        notification_data = get_base_notification_data()
        notification = generate_raw_notification(notification_data, self.source.name)

        mock_receive_notifications.return_value = [notification]

        res = get_notifications(self.logger, NotificationSource.objects.all())

        self.assertEqual(1, len(res))
        self.logger.log_warning.assert_not_called()

    @patch("nautobot_circuit_maintenance.handle_notifications.sources.GmailAPI.receive_notifications")
    def test_get_notifications_multiple(self, mock_receive_notifications):
        """Test get_notifications multiple."""
        notification_data = get_base_notification_data()
        notification = generate_raw_notification(notification_data, self.source.name)

        mock_receive_notifications.return_value = [notification, notification]

        res = get_notifications(self.logger, NotificationSource.objects.all())

        self.assertEqual(2, len(res))
        self.logger.log_warning.assert_not_called()

    @parameterized.expand(
        [
            ["name_1", "url1", "user_1", "credentials_file", False],
            ["name_1", "url1", None, "credentials_file", True],
            ["name_1", "url1", "user_1", None, True],
        ]  # pylint: disable=too-many-arguments
    )
    def test_gmail_api_service_account_init(self, name, url, account, credentials_file, exception):
        """Test Gmail API class init."""
        kwargs = {}
        if name:
            kwargs["name"] = name
        if url:
            kwargs["url"] = url
        if account:
            kwargs["account"] = account
        if credentials_file:
            kwargs["credentials_file"] = credentials_file

        if exception:
            with self.assertRaises(ValidationError):
                GmailAPI(**kwargs)
        else:
            GmailAPI(**kwargs)

    @patch("nautobot_circuit_maintenance.handle_notifications.sources.GmailAPI.load_credentials")
    def test_gmail_api_test_authentication_ok(self, mock_credentials):  # pylint: disable=unused-argument
        source = GmailAPI(
            name="whatever",
            url="https://accounts.google.com/o/oauth2/auth",
            account="account",
            credentials_file="path_to_file",
        )
        res, message = source.test_authentication()
        self.assertEqual(res, True)
        self.assertEqual(message, "Test OK")

    @patch("nautobot_circuit_maintenance.handle_notifications.sources.GmailAPI.load_credentials")
    def test_gmail_api_test_authentication_ko(self, mock_credentials):  # pylint: disable=unused-argument
        mock_credentials.side_effect = Exception("error message")
        source = GmailAPI(
            name="whatever",
            url="https://accounts.google.com/o/oauth2/auth",
            account="account",
            credentials_file="path_to_file",
        )
        res, message = source.test_authentication()
        self.assertEqual(res, False)
        self.assertEqual(message, "error message")

    @staticmethod
    def email_setup():
        """Helper method for several test cases below."""
        provider = Provider.objects.create(name="zayo", slug="zayo")
        provider.cf["emails_circuit_maintenances"] = "user@example.com"
        provider.save()

        job = Job()
        job.job_result = JobResult.objects.create(
            name="dummy", obj_type=ContentType.objects.get_for_model(JobModel), user=None, job_id=uuid.uuid4()
        )

        source = GmailAPI(
            name="whatever",
            url="https://accounts.google.com/o/oauth2/auth",
            account="account",
            credentials_file="path_to_file",
        )

        return (provider, job, source)

    def test_process_email_success(self):
        """Test successful processing of a single email into a MaintenanceNotification."""
        provider, job, source = self.email_setup()

        received_email = {
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Circuit Maintenance Notification"},
                    {"name": "From", "value": "user@example.com"},
                ],
                "parts": [
                    {
                        "headers": [{"name": "Content-Type", "value": "text/html"}],
                        "body": {"data": base64.b64encode(b"Some text goes here")},
                    }
                ],
            },
            "internalDate": 1000,
        }

        notification = source.process_email(job, received_email, msg_id="abc", since=0)
        self.assertIsNotNone(notification)
        self.assertEqual(notification.source, source.name)
        self.assertEqual(notification.sender, "user@example.com")
        self.assertEqual(notification.subject, "Circuit Maintenance Notification")
        self.assertEqual(notification.provider_type, provider.slug)
        self.assertEqual(list(notification.raw_payloads), [b"Some text goes here"])

    def test_process_email_success_alternate_source_header(self):
        """Test successful processing of a single email with a non-standard source header."""
        provider, job, source = self.email_setup()

        source.source_header = "X-Original-Sender"

        received_email = {
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Circuit Maintenance Notification"},
                    {"name": "From", "value": "mailing-list@example.com"},
                    {"name": "X-Original-Sender", "value": "user@example.com"},
                ],
                "parts": [
                    {
                        "headers": [{"name": "Content-Type", "value": "text/html"}],
                        "body": {"data": base64.b64encode(b"Some text goes here")},
                    }
                ],
            },
            "internalDate": 1000,
        }

        notification = source.process_email(job, received_email, msg_id="abc", since=0)
        self.assertIsNotNone(notification)
        self.assertEqual(notification.source, source.name)
        self.assertEqual(notification.sender, "user@example.com")
        self.assertEqual(notification.subject, "Circuit Maintenance Notification")
        self.assertEqual(notification.provider_type, provider.slug)
        self.assertEqual(list(notification.raw_payloads), [b"Some text goes here"])
