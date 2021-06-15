"""Notification Source classes."""
import re
import datetime
import email
import imaplib
from urllib.parse import urlparse
from email.utils import mktime_tz, parsedate_tz
from typing import Iterable, Optional, TypeVar, Type, Tuple

from django.conf import settings

from pydantic import BaseModel  # pylint: disable=no-name-in-module
from pydantic.error_wrappers import ValidationError  # pylint: disable=no-name-in-module
from circuit_maintenance_parser import NonexistentParserError, MaintenanceNotification, get_provider_data_type
from nautobot.circuits.models import Provider
from nautobot.extras.jobs import Job
from nautobot.extras.models import CustomField

from nautobot_circuit_maintenance.models import NotificationSource

# pylint: disable=broad-except

T = TypeVar("T", bound="Source")  # pylint: disable=invalid-name


class Source(BaseModel):
    """Base class to retrieve notifications. To be extended for each scheme."""

    name: str
    url: str

    def receive_notifications(self, logger: Job, since: int = None) -> Iterable[MaintenanceNotification]:
        """Function to retrieve notifications since one moment in time.

        The `MaintenanceNotification` attributes will contains these attributes:
        * source: self.name
        * sender: it could be the email 'from' or omitted if not relevant
        * subject: it could be the email 'subject' or some meaningful identifier from notification
        * raw: the raw_payload from notification
        * provider_type: the provider slug identified by sender email or from membership
        """
        # TODO: `senders` is used to limit the scope of emails retrieved, this won't have sense depending on the
        # Notification Source.
        raise NotImplementedError

    def validate_providers(self, logger: Job, notification_source: NotificationSource, since_txt: str) -> bool:
        """Method to validate that the NotificationSource has attached Providers.

        Args:
            logger (Job): Job to use its logger
            notification_source (NotificationSource): Notification Source to validate providers
            since_txt (str): Date string to be used to log

        Returns:
            bool: True if there are relevant providers attached or False otherwise
        """
        raise NotImplementedError

    def test_authentication(self) -> Tuple[bool, str]:
        """Method to validate the authentication of the Source.

        Returns:
            Tuple:
                bool: True if authentication was successful, False otherwise
                str: Message from authentication execution
        """
        raise NotImplementedError

    @classmethod
    def init(cls: Type[T], name: str) -> Type[T]:
        """Factory Pattern to get the specific Source Class depending on the scheme."""
        for notification_source in settings.PLUGINS_CONFIG.get("nautobot_circuit_maintenance", {}).get(
            "notification_sources", []
        ):
            if notification_source.get("name", "") == name:
                config = notification_source
                break
        else:
            raise ValueError(f"Name {name} not found in PLUGINS_CONFIG.")

        url = config.get("url")
        if not url:
            raise ValueError(f"URL for {name} not found in PLUGINS_CONFIG.")

        url_components = urlparse(url)
        scheme = url_components.scheme.lower()
        if scheme == "imap":
            return IMAP(
                name=name,
                url=url,
                user=config.get("account"),
                password=config.get("secret"),
                imap_server=url_components.netloc.split(":")[0],
                imap_port=url_components.port or 993,
            )

        raise ValueError(f"Scheme {scheme} not supported as Notification Source (only IMAP).")


class IMAP(Source):
    """IMAP class, extending Source class."""

    user: str
    password: str
    imap_server: str
    imap_port: int = 993

    session: Optional[imaplib.IMAP4_SSL] = None
    emails_to_fetch = []

    class Config:
        """Pydantic BaseModel config."""

        arbitrary_types_allowed = True

    def open_session(self):
        """Open session to IMAP server."""
        if not self.session:
            self.session = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.session.login(self.user, self.password)

    def close_session(self):
        """Close session to IMAP server."""
        if self.session:
            if self.session.state == "SELECTED":
                self.session.close()
            if self.session.state == "AUTH":
                self.session.logout()

    def test_authentication(self) -> Tuple[bool, str]:
        """Method to validate the authentication of the Source.

        Returns:
            Tuple:
                bool: True if authentication was successful, False otherwise
                str: Message from authentication execution
        """
        try:
            self.open_session()
            self.close_session()
            is_authenticated = True
            message = "Test OK"
        except Exception as exc:
            is_authenticated = False
            if isinstance(exc.args[0], bytes):
                message = str(exc.args[0].decode())
            else:
                message = str(exc)
        return is_authenticated, message

    # pylint: disable=inconsistent-return-statements
    def fetch_email(self, logger: Job, msg_id: bytes, since: Optional[int]) -> Optional[MaintenanceNotification]:
        """Fetch an specific email ID."""
        _, data = self.session.fetch(msg_id, "(RFC822)")
        raw_email = data[0][1]
        raw_email_string = raw_email.decode("utf-8")
        email_message = email.message_from_string(raw_email_string)

        if since:
            if mktime_tz(parsedate_tz(email_message["Date"])) < since:
                logger.log_info(message=f"'{email_message['Subject']}' email is old, so not taking into account.")
                return

        try:
            email_source = re.search(r"\<([A-Za-z0-9_@.]+)\>", email_message["From"]).group(1)
        except AttributeError:
            try:
                email_source = re.search(r"([A-Za-z0-9_@.]+)", email_message["From"]).group(1)
            except AttributeError:
                logger.log_failure(
                    email_message, f"Not possible to determine the email sender: {email_message['From']}"
                )
                return

        for provider in Provider.objects.all():
            if "emails_circuit_maintenances" in provider.custom_field_data:
                if email_source in provider.custom_field_data["emails_circuit_maintenances"].split(","):
                    provider_type = provider.slug
                    break
        else:
            logger.log_warning(
                message=f"Sender email {email_source} is not registered for any circuit provider.",
            )
            return

        try:
            provider_data_type = get_provider_data_type(provider_type)
        except NonexistentParserError:
            logger.log_warning(
                message=f"Unexpected provider {provider_type} received from {email_message['From']}, so not getting the notification",
            )
            return

        for part in email_message.walk():
            if part.get_content_type() == provider_data_type:
                raw_payload = part.get_payload()
                break
        else:
            logger.log_warning(
                message=f"Payload type {provider_data_type} not found in email payload.",
            )
            return

        return MaintenanceNotification(
            source=self.name,
            sender=email_message["From"],
            subject=email_message["Subject"],
            raw=raw_payload,
            provider_type=provider_type,
        )

    def receive_notifications(self, logger: Job, since: int = None) -> Iterable[MaintenanceNotification]:
        """Retrieve emails since an specific time, if provided."""
        self.open_session()

        # Define searching criteria
        self.session.select("Inbox")

        # TODO: find the right way to search messages from several senders
        # Maybe extend filtering options, for instance, to discard some type of notifications
        msg_ids = []
        since_date = ""
        if since:
            # IMAP search time criteria does not work for hours/minutes/seconds
            since_txt = datetime.datetime.fromtimestamp(since).strftime("%d-%b-%Y")
            since_date = f'SINCE "{since_txt}"'

        if self.emails_to_fetch:
            for sender in self.emails_to_fetch:
                search_items = (f'FROM "{sender}"', since_date)
                search_text = " ".join(search_items).strip()
                search_criteria = f"({search_text})"
                messages = self.session.search(None, search_criteria)[1][0]
                msg_ids.extend(messages.split())
        else:
            search_criteria = f"({since_date})"
            messages = self.session.search(None, search_criteria)[1][0]
            msg_ids.extend = messages.split()

        received_notifications = []

        for msg_id in msg_ids:
            raw_notification = self.fetch_email(logger, msg_id, since)
            if raw_notification:
                received_notifications.append(raw_notification)

        self.close_session()
        return received_notifications

    def validate_providers(self, logger: Job, notification_source: NotificationSource, since_txt: str) -> bool:
        """Method to validate that the NotificationSource has attached Providers.

        Args:
            logger (Job): Job to use its logger
            notification_source (NotificationSource): Notification Source to validate providers
            since_txt (str): Date string to be used to log

        Returns:
            bool: True if there are relevant providers attached or False otherwise
        """
        providers_with_email = []
        providers_without_email = []
        if not notification_source.providers.all():
            logger.log_warning(
                message="Skipping this email account no providers were defined.",
            )
            return False

        for provider in notification_source.providers.all():
            cm_cf = CustomField.objects.get(name="emails_circuit_maintenances")
            provider_emails = provider.get_custom_fields().get(cm_cf)
            if provider_emails:
                self.emails_to_fetch.extend(provider_emails.split(","))
                providers_with_email.append(provider.name)
            else:
                providers_without_email.append(provider.name)

        if providers_without_email:
            logger.log_warning(
                message=(
                    f"Skipping {', '.join(providers_without_email)} because these providers have no email configured."
                ),
            )

        if not providers_with_email:
            logger.log_warning(
                message=(
                    f"Skipping Notification Source {notification_source.name} because none of the related providers "
                    "have emails defined."
                ),
            )
            return False

        logger.log_info(
            message=(
                f"Retrieving notifications from {notification_source.name} for "
                f"{', '.join(providers_with_email)} since {since_txt}"
            ),
        )

        return True


def get_notifications(
    logger: Job, notification_sources: Iterable[NotificationSource], since: int = None
) -> Iterable[MaintenanceNotification]:
    """Method to fetch notifications from multiple sources and return MaintenanceNotification objects."""
    received_notifications = []

    for notification_source in notification_sources:
        try:
            if since:
                since_txt = datetime.datetime.fromtimestamp(since).strftime("%d-%b-%Y")
            else:
                since_txt = "always"

            try:
                source = Source.init(name=notification_source.name)
            except ValidationError as validation_error:
                logger.log_warning(
                    message=(
                        f"Notification Source {notification_source.name} is not matching class expectations: "
                        f"{validation_error}"
                    ),
                )
                continue
            except ValueError as value_error:
                logger.log_warning(message=value_error)
                continue

            if source.validate_providers(logger, notification_source, since_txt):
                raw_notifications = source.receive_notifications(logger, since)
                received_notifications.extend(raw_notifications)

                if not raw_notifications:
                    logger.log_info(
                        message=(
                            f"No notifications received for "
                            f"{', '.join(notification_source.providers.all().values_list('name', flat=True))} since "
                            f"{since_txt} from {notification_source.name}"
                        ),
                    )

        except Exception as error:
            logger.log_warning(
                message=f"Issue fetching notifications from {notification_source.name}: {error}",
            )

    return received_notifications
