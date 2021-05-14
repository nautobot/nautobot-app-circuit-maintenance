"""Email helper functions."""
import re
import datetime
import email
import imaplib
from email.utils import mktime_tz, parsedate_tz
from typing import Iterable, Optional, Union

from pydantic import BaseModel  # pylint: disable=no-name-in-module
from circuit_maintenance_parser import NonexistentParserError, MaintenanceNotification, get_provider_data_type
from nautobot.circuits.models import Provider
from nautobot_circuit_maintenance.models import NotificationSource

# pylint: disable=broad-except


class Email(BaseModel):
    """Base class to retrieve emails. To be extended for each email protocol."""

    def receive_emails(self, senders: Iterable[str] = None, since: int = None) -> Iterable[MaintenanceNotification]:
        """Function to retrieve emails."""


class IMAP(BaseModel):
    """IMAP class."""

    service: str
    user: str
    password: str
    imap_url: str

    session: Union[imaplib.IMAP4_SSL, None] = None

    class Config:
        """Pydantic BaseModel config."""

        arbitrary_types_allowed = True

    def __post_init__(self):
        """Post init validation."""
        if self.user is None:
            raise AssertionError(
                f"User for {self.service} is not present as environmental variable {self.service}_USER"
            )
        if self.password is None:
            raise AssertionError(
                f"Password for {self.service} is not present as environmental variable {self.service}_PWD"
            )
        if self.imap_url is None:
            raise AssertionError(
                f"IMAP URL for {self.service} is not present as environmental variable {self.service}_IMAP"
            )

    def open_session(self):
        """Open session to IMAP server."""
        if not self.session:
            self.session = imaplib.IMAP4_SSL(self.imap_url)
            self.session.login(self.user, self.password)

    def close_session(self):
        """Close session to IMAP server."""
        if self.session:
            if self.session.state == "SELECTED":
                self.session.close()
            if self.session.state == "AUTH":
                self.session.logout()

    # pylint: disable=inconsistent-return-statements
    def fetch_email(self, logger, msg_id: bytes, since: Optional[int]) -> Optional[MaintenanceNotification]:
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
            source=self.service,
            sender=email_message["From"],
            subject=email_message["Subject"],
            raw=raw_payload,
            provider_type=provider_type,
        )

    def receive_emails(
        self, logger, senders: Iterable[str] = None, since: int = None
    ) -> Iterable[MaintenanceNotification]:
        """Retrieve emails from specific senders and from an specific time, if provided."""
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

        if senders:
            for sender in senders:
                search_items = (f'FROM "{sender}"', since_date)
                search_text = " ".join(search_items).strip()
                search_criteria = f"({search_text})"
                messages = self.session.search(None, search_criteria)[1][0]
                msg_ids.extend(messages.split())
        else:
            search_criteria = f"({since_date})"
            messages = self.session.search(None, search_criteria)[1][0]
            msg_ids.extend = messages.split()

        received_emails = []

        for msg_id in msg_ids:
            raw_notification = self.fetch_email(logger, msg_id, since)
            if raw_notification:
                received_emails.append(raw_notification)

        self.close_session()
        return received_emails


def get_notifications_from_email(
    logger, email_boxes: Iterable[NotificationSource], since: int = None
) -> Iterable[MaintenanceNotification]:
    """Method to fetch email from multiple sources and return MaintenanceNotification objects."""
    received_notifications = []

    for email_box in email_boxes:
        try:
            if since:
                since_txt = datetime.datetime.fromtimestamp(since).strftime("%d-%b-%Y")
            else:
                since_txt = "always"

            restrict_emails = []

            providers_with_email = []
            providers_without_email = []
            if not email_box.providers.all():
                logger.log_warning(
                    message="Skipping this email account no providers were defined.",
                )
                continue

            for provider in email_box.providers.all():
                for custom_field, value in provider.get_custom_fields().items():
                    if custom_field.name == "emails_circuit_maintenances" and value:
                        restrict_emails.extend(value.split(","))
                        providers_with_email.append(provider.name)
                    else:
                        providers_without_email.append(provider.name)

            if providers_without_email:
                logger.log_warning(
                    message=f"Skipping {', '.join(providers_without_email)} because these providers has no email configured.",
                )

            if not providers_with_email:
                logger.log_warning(
                    message=f"Skipping this email account because none of the providers ({', '.join(providers_with_email)}) have at least one email defined.",
                )
                continue

            logger.log_info(
                message=f"Retrieving notifications from {email_box.source_id} for {', '.join(providers_with_email)} since {since_txt}",
            )
            imap_conn = IMAP(
                service=email_box.source_type.lower(),
                user=email_box.source_id,
                # How to setup GMAIL APP password
                # https://support.google.com/accounts/answer/185833
                password=email_box._password,  # pylint: disable=protected-access
                imap_url=email_box.url,
            )
            rawnotification = imap_conn.receive_emails(logger, restrict_emails, since)
            received_notifications.extend(rawnotification)

            if not received_notifications:
                logger.log_info(
                    message=f"No notifications received for {', '.join(providers_with_email)} since {since_txt} from {email_box.source_id}",
                )
        except Exception as error:
            logger.log_warning(
                message=f"Issue fetching notifications from {email_box.source_id}: {error}",
            )

    return received_notifications
