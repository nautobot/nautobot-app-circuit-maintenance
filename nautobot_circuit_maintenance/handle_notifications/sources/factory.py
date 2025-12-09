"""Factory for Source classes and notification fetching."""

import datetime
import json
import os
from typing import Iterable
from urllib.parse import urlparse

from django.conf import settings
from nautobot.extras.jobs import Job
from pydantic import ValidationError

try:
    import exchangelib

    EXCHANGELIB_PRESENT = True
except ImportError:
    EXCHANGELIB_PRESENT = False

from nautobot_circuit_maintenance.models import NotificationSource

from .base import Source
from .ews import ExchangeWebService
from .gmail import GmailAPIOauth, GmailAPIServiceAccount
from .imap import IMAP
from .maintenance_notification import MaintenanceNotification


def init_source(name: str) -> Source:  # pylint: disable=too-many-branches
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
            account=config.get("account"),
            password=config.get("secret"),
            imap_server=url_components.netloc.split(":")[0],
            imap_port=url_components.port or 993,
            source_header=config.get("source_header", "From"),
        )
    if scheme == "ews":
        if not EXCHANGELIB_PRESENT:
            raise ValueError("You must install 'exchangelib' to use the 'ews' scheme.")

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
    if scheme == "https" and url_components.netloc.split(":")[0] == "accounts.google.com":
        creds_filename = config.get("credentials_file")
        if not creds_filename:
            raise ValueError(f"Credentials_file for {name} not found in PLUGINS_CONFIG.")

        if not os.path.isfile(creds_filename):
            raise ValueError(f"Credentials_file {creds_filename} for {name} is not available.")

        with open(creds_filename, encoding="utf-8") as credentials_file:
            credentials = json.load(credentials_file)
            if credentials.get("type") == "service_account":
                gmail_api_class = GmailAPIServiceAccount
            elif "web" in credentials:
                gmail_api_class = GmailAPIOauth
            else:
                raise NotImplementedError(f"File {creds_filename} doens't contain any supported credentials.")
            return gmail_api_class(
                name=name,
                url=url,
                account=config.get("account"),
                credentials_file=creds_filename,
                source_header=config.get("source_header", "From"),
                limit_emails_with_not_header_from=config.get("limit_emails_with_not_header_from", []),
                extra_scopes=config.get("extra_scopes", []),
                labels=config.get("labels", {}),
            )

    raise ValueError(
        f"Scheme {scheme} not supported as Notification Source (only IMAP or HTTPS to accounts.google.com)."
    )


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
                source = init_source(name=notification_source.name)
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
