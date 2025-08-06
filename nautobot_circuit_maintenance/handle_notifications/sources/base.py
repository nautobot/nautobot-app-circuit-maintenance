"""Notification Source classes."""

import datetime
import json
import os
from typing import Iterable, Tuple, Union
from urllib.parse import urlparse

from django.conf import settings
from nautobot.extras.jobs import Job
from pydantic import BaseModel, ValidationError

try:
    import exchangelib

    EXCHANGELIB_PRESENT = True
except ImportError:
    EXCHANGELIB_PRESENT = False

from nautobot_circuit_maintenance.enum import MessageProcessingStatus
from nautobot_circuit_maintenance.models import NotificationSource
from .exceptions import RedirectAuthorize

from .maintenance_notification import MaintenanceNotification

# pylint: disable=broad-except


class Source(BaseModel):
    """Base class to retrieve notifications. To be extended for each scheme."""

    name: str
    url: str

    def get_account_id(self) -> str:
        """Method to get an identifier of the related account."""
        raise NotImplementedError

    def receive_notifications(
        self, job: Job, since_timestamp: datetime.datetime = None
    ) -> Iterable[MaintenanceNotification]:
        """Function to retrieve notifications since one moment in time.

        The `MaintenanceNotification` attributes will contains these attributes:
        * source: self.name
        * sender: it could be the email 'from' or omitted if not relevant
        * subject: it could be the email 'subject' or some meaningful identifier from notification
        * provider_type: mapping to the Provider that is related to this notification
        * raw: the raw_payload from notification
        """
        # TODO: `senders` is used to limit the scope of emails retrieved, this won't have sense depending on the
        # Notification Source.
        raise NotImplementedError

    def validate_providers(
        self, job: Job, notification_source: NotificationSource, since_txt: str
    ) -> bool:
        """Method to validate that the NotificationSource has attached Providers.

        Args:
            job (Job): Job to use its logger
            notification_source (NotificationSource): Notification Source to validate providers
            since_txt (str): Date string to be used to log

        Returns:
            bool: True if there are relevant providers attached or False otherwise
        """
        raise NotImplementedError

    def _authentication_logic(self):
        """Inner method to run the custom class validation logic."""
        raise NotImplementedError

    def test_authentication(self) -> Tuple[bool, str]:
        """Method to validate the authentication of the Source.

        Returns:
            Tuple:
                bool: True if authentication was successful, False otherwise
                str: Message from authentication execution
        """
        try:
            self._authentication_logic()
            is_authenticated = True
            message = "Test OK"
        except RedirectAuthorize:
            raise
        except Exception as exc:
            is_authenticated = False
            if isinstance(exc.args[0], bytes):
                message = str(exc.args[0].decode())
            else:
                message = str(exc)

        return is_authenticated, message

    @staticmethod
    def init(name: str) -> "Source":  # pylint: disable=too-many-branches
        """Factory Pattern to get the specific Source Class depending on the scheme."""
        for notification_source in settings.PLUGINS_CONFIG.get(
            "nautobot_circuit_maintenance", {}
        ).get("notification_sources", []):
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
            from .imap import IMAP  # pylint: disable=import-outside-toplevel

            return IMAP(
                name=name,
                url=url,
                account=config.get("account"),
                password=config.get("secret"),
                imap_server=url_components.netloc.split(":")[0],
                imap_port=url_components.port or 993,
                source_header=config.get("source_header", "From"),
            )
        if scheme == "ews":
            if not EXCHANGELIB_PRESENT:
                raise ValueError(
                    "You must install 'exchangelib' to use the 'ews' scheme."
                )
            from .ews import (  # pylint: disable=import-outside-toplevel
                ExchangeWebService,
            )

            return ExchangeWebService(
                name=name,
                url=url,
                account=config.get("account"),
                authentication_user=config.get("authentication_user"),
                password=config.get("secret"),
                access_type=config.get("access_type", exchangelib.DELEGATE),
                folder=config.get("folder"),
                server=url_components.netloc.split(":")[0],
            )
        if (
            scheme == "https"
            and url_components.netloc.split(":")[0] == "accounts.google.com"
        ):
            creds_filename = config.get("credentials_file")
            if not creds_filename:
                raise ValueError(
                    f"Credentials_file for {name} not found in PLUGINS_CONFIG."
                )

            if not os.path.isfile(creds_filename):
                raise ValueError(
                    f"Credentials_file {creds_filename} for {name} is not available."
                )

            with open(creds_filename, encoding="utf-8") as credentials_file:
                credentials = json.load(credentials_file)
                if credentials.get("type") == "service_account":
                    from .gmail import (  # pylint: disable=import-outside-toplevel
                        GmailAPIServiceAccount,
                    )

                    gmail_api_class = GmailAPIServiceAccount
                elif "web" in credentials:
                    from .gmail import (  # pylint: disable=import-outside-toplevel
                        GmailAPIOauth,
                    )

                    gmail_api_class = GmailAPIOauth
                else:
                    raise NotImplementedError(
                        f"File {creds_filename} doens't contain any supported credentials."
                    )
                return gmail_api_class(
                    name=name,
                    url=url,
                    account=config.get("account"),
                    credentials_file=creds_filename,
                    source_header=config.get("source_header", "From"),
                    limit_emails_with_not_header_from=config.get(
                        "limit_emails_with_not_header_from", []
                    ),
                    extra_scopes=config.get("extra_scopes", []),
                    labels=config.get("labels", {}),
                )

        raise ValueError(
            f"Scheme {scheme} not supported as Notification Source (only IMAP or HTTPS to accounts.google.com)."
        )

    def tag_message(
        self, job: Job, msg_id: Union[str, bytes], tag: MessageProcessingStatus
    ):
        """If supported, apply the given tag to the given message for future reference and categorization.

        The default implementation of this method is a no-op but specific Source subclasses may implement it.
        """


def get_notifications(
    job: Job,
    notification_sources: Iterable[NotificationSource],
    since: int,
) -> Iterable[MaintenanceNotification]:
    """Method to fetch notifications from multiple sources and return MaintenanceNotification objects."""
    received_notifications = []

    for notification_source in notification_sources:
        try:
            since_date = datetime.datetime.fromtimestamp(since)
            since_txt = since_date.strftime("%d-%b-%Y")

            try:
                source = Source.init(name=notification_source.name)
            except ValidationError as validation_error:
                job.logger.warning(
                    (
                        f"Notification Source {notification_source.name} "
                        f"is not matching class expectations: {validation_error}"
                    ),
                    extra={"object": notification_source},
                    exc_info=True,
                )
                continue
            except ValueError:
                job.logger.warning(
                    f"Skipping notification source {notification_source}",
                    extra={"object": notification_source},
                    exc_info=True,
                )
                continue

            if source.validate_providers(job, notification_source, since_txt):
                if since_date:
                    # When using the SINCE filter, we add one extra day to check for notifications received
                    # on the very same day since last notification.
                    since_date -= datetime.timedelta(days=1)

                raw_notifications = source.receive_notifications(job, since_date)
                received_notifications.extend(raw_notifications)

                if not raw_notifications:
                    job.logger.info(
                        (
                            f"No notifications received for "
                            f"{', '.join(notification_source.providers.all().values_list('name', flat=True))} since "
                            f"{since_txt} from {notification_source.name}"
                        ),
                        extra={"object": notification_source},
                    )

        except Exception:
            job.logger.error(
                f"Issue fetching notifications from {notification_source.name}",
                extra={"object": notification_source},
                exc_info=True,
            )
            raise

    return received_notifications
