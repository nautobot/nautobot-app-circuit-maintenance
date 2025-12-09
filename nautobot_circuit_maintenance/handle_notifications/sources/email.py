"""Generic Email Source."""

import email
import re
from typing import List, Optional, Union

from nautobot.circuits.models import Provider
from nautobot.extras.jobs import Job

from nautobot_circuit_maintenance.enum import MessageProcessingStatus
from nautobot_circuit_maintenance.models import NotificationSource

from .base import Source
from .maintenance_notification import MaintenanceNotification


class EmailSource(Source):  # pylint: disable=abstract-method
    """Abstract class that shares some methods and attributes across email based sources."""

    account: str
    emails_to_fetch: List[str] = []
    source_header: str = "From"

    def get_account_id(self) -> str:
        """Method to get an identifier of the related account."""
        return self.account

    def validate_providers(self, job: Job, notification_source: NotificationSource, since_txt: str) -> bool:
        """Method to validate that the NotificationSource has attached Providers.

        Args:
            job (Job): Job to use its logger
            notification_source (NotificationSource): Notification Source to validate providers
            since_txt (str): Date string to be used to log

        Returns:
            bool: True if there are relevant providers attached or False otherwise
        """
        providers_with_email = []
        providers_without_email = []
        if not notification_source.providers.all():
            job.logger.warning(
                f"Skipping source '{notification_source.name}' because no providers were defined.",
                extra={"object": notification_source},
            )
            return False

        for provider in notification_source.providers.all():
            provider_emails = provider.cf.get("emails_circuit_maintenances")
            if provider_emails:
                self.emails_to_fetch.extend([src.strip().lower() for src in provider_emails.split(",")])
                providers_with_email.append(provider.name)
            else:
                providers_without_email.append(provider.name)

        if providers_without_email:
            job.logger.warning(
                f"Skipping {', '.join(providers_without_email)} because these providers have no email configured.",
                extra={"object": notification_source},
            )

        if not providers_with_email:
            job.logger.warning(
                (
                    f"Skipping Notification Source {notification_source.name} because none of the related providers "
                    "have emails defined."
                ),
                extra={"object": notification_source},
            )
            return False
        job.logger.debug(f"Fetching emails from {self.emails_to_fetch}")
        job.logger.info(
            (
                f"Retrieving notifications from {notification_source.name} for "
                f"{', '.join(providers_with_email)} since {since_txt}"
            ),
            extra={"object": notification_source},
        )

        return True

    @staticmethod
    def extract_email_source(email_source: str) -> str:
        """Method to get the sender email address."""
        try:
            email_source = re.search(r"\<([-A-Za-z0-9_@.]+)\>", email_source).group(1)
        except AttributeError:
            try:
                email_source = re.search(r"([-A-Za-z0-9_@.]+)", email_source).group(1)
            except AttributeError:
                return ""
        return email_source.lower()

    @staticmethod
    def get_provider_type_from_email(email_source: str) -> Optional[str]:
        """Return the `Provider` type related to the source."""
        for provider in Provider.objects.all():
            emails_for_provider = provider.cf.get("emails_circuit_maintenances")
            if not emails_for_provider:
                continue
            sources = [src.strip().lower() for src in emails_for_provider.split(",")]
            if email_source in sources:
                return provider.name
        return None

    def process_email(
        self,
        job: Job,
        email_message: email.message.EmailMessage,
        msg_id: Union[str, bytes],
    ) -> Optional[MaintenanceNotification]:
        """Process an EmailMessage to create the MaintenanceNotification."""
        email_source = None
        if email_message[self.source_header]:
            email_source = self.extract_email_source(email_message[self.source_header])

        if not email_source:
            job.logger.error(
                (
                    "Not possible to determine the email sender from "
                    f'"{self.source_header}: {email_message[self.source_header]}"',
                ),
                extra={"object": email_message},
            )
            self.tag_message(job, msg_id, MessageProcessingStatus.UNKNOWN_PROVIDER)
            raise ValueError("Not possible to determine the email sender.")

        provider_type = self.get_provider_type_from_email(email_source)
        if not provider_type:
            job.logger.warning(
                f"Not possible to determine the provider_type for {email_source}",
                extra={"object": email_source},
            )
            self.tag_message(job, msg_id, MessageProcessingStatus.UNKNOWN_PROVIDER)
            return None

        return MaintenanceNotification(
            source=self,
            sender=email_source,
            subject=email_message["Subject"],
            provider_type=provider_type,
            raw_payload=email_message.as_bytes(),
            date=email_message["Date"],
            msg_id=msg_id,
        )
