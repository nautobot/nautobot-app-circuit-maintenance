"""ExchangeWebService Source."""

import datetime
from typing import Iterable, Optional

from pydantic import Field

try:
    import exchangelib

    EXCHANGELIB_PRESENT = True
except ImportError:
    EXCHANGELIB_PRESENT = False

from nautobot.extras.jobs import Job

from nautobot_circuit_maintenance.enum import MessageProcessingStatus

from .email import EmailSource
from .maintenance_notification import MaintenanceNotification


class ExchangeWebService(EmailSource):
    """Microsoft EWS class, extending Source class."""

    access_type: str
    authentication_user: str
    password: str = Field(repr=False)
    server: str
    folder: Optional[str] = None
    session: Optional["exchangelib.Account"] = None

    class Config:
        """Pydantic BaseModel config."""

        arbitrary_types_allowed = True

    def open_session(self):
        """Open session to EWS server."""
        if not EXCHANGELIB_PRESENT:
            raise RuntimeError("You must install 'exchangelib' to use this source")
        if not self.session:
            credentials = exchangelib.Credentials(
                username=self.authentication_user,
                password=self.password,
            )
            config = exchangelib.Configuration(
                server=self.server,
                credentials=credentials,
            )
            self.session = exchangelib.Account(
                primary_smtp_address=self.account,
                config=config,
                autodiscover=True,
                access_type=self.access_type,
            )

    def close_session(self):
        """Close session to EWS server."""
        if self.session:
            self.session.protocol.close()
            self.session = None

    def _authentication_logic(self):
        """Inner method to run the custom class validation logic."""
        self.open_session()
        self.close_session()

    def receive_notifications(
        self, job: Job, since_timestamp: datetime.datetime = None
    ) -> Iterable[MaintenanceNotification]:
        """Retrieve emails since an specific time, if provided."""
        self.open_session()

        mailbox = self.session.inbox
        if self.folder:
            mailbox = mailbox / self.folder

        # Filter emails by sender.
        mailbox = mailbox.filter(sender__in=self.emails_to_fetch)

        # Filter emails by timestamp.
        if since_timestamp:
            epoch = int(since_timestamp.strftime("%s"))
            since_time = exchangelib.EWSDateTime.fromtimestamp(epoch, tz=exchangelib.UTC)
            mailbox = mailbox.filter(datetime_received__gte=since_time)

        job.logger.debug(message=f"Fetched {mailbox.count()} emails from {self.name} source.")

        received_notifications = [self.get_notification_from_item(job, item) for item in mailbox]
        job.logger.debug(message=f"Raw notifications created {len(received_notifications)} from {self.name}.")

        self.close_session()
        return received_notifications

    def get_notification_from_item(
        self,
        job: Job,
        item: "exchangelib.items.message.Message",
    ) -> Optional[MaintenanceNotification]:
        """Return a MaintenanceNotification derived from a give email item."""
        msg_id = item.id
        email_source = item.sender.email_address

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
            subject=item.subject,
            provider_type=provider_type,
            raw_payload=item.mime_content,
            date=str(item.datetime_created),
            msg_id=msg_id,
        )
