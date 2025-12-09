"""IMAP source."""

import datetime
import email
import imaplib
from typing import Iterable, Optional

from nautobot.extras.jobs import Job
from pydantic import Field

from .email import EmailSource
from .maintenance_notification import MaintenanceNotification


class IMAP(EmailSource):
    """IMAP class, extending Source class."""

    password: str = Field(repr=False)
    imap_server: str
    imap_port: int = 993

    session: Optional[imaplib.IMAP4_SSL] = None

    class Config:
        """Pydantic BaseModel config."""

        arbitrary_types_allowed = True

    def open_session(self):
        """Open session to IMAP server.

        See states: https://github.com/python/cpython/blob/3.9/Lib/imaplib.py#L58
        """
        if not self.session:
            self.session = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        if self.session.state == "NONAUTH":
            self.session.login(self.account, self.password)

    def close_session(self):
        """Close session to IMAP server.

        See states: https://github.com/python/cpython/blob/3.9/Lib/imaplib.py#L58
        """
        if self.session:
            if self.session.state == "SELECTED":
                self.session.close()
            if self.session.state == "AUTH":
                self.session.logout()

    def _authentication_logic(self):
        """Inner method to run the custom class validation logic."""
        self.open_session()
        self.close_session()

    def fetch_email(self, job: Job, msg_id: bytes) -> Optional[MaintenanceNotification]:
        """Fetch an specific email ID."""
        _, data = self.session.fetch(msg_id, "(RFC822)")
        email_message = email.message_from_bytes(data[0][1])

        return self.process_email(job, email_message, msg_id)

    def receive_notifications(
        self, job: Job, since_timestamp: datetime.datetime = None
    ) -> Iterable[MaintenanceNotification]:
        """Retrieve emails since an specific time, if provided."""
        self.open_session()

        # Define searching criteria
        self.session.select("Inbox")

        # TODO: find the right way to search messages from several senders
        # Maybe extend filtering options, for instance, to discard some type of notifications
        msg_ids = []

        # TODO: define a similar function to _get_search_criteria
        since_date = ""
        if since_timestamp:
            since_txt = since_timestamp.strftime("%d-%b-%Y")
            since_date = f'SINCE "{since_txt}"'

        if self.emails_to_fetch:
            for sender in self.emails_to_fetch:
                if self.source_header == "From":
                    search_items = (f'FROM "{sender}"', since_date)
                else:
                    search_items = (
                        f'HEADER {self.source_header} "{sender}"',
                        since_date,
                    )
                search_text = " ".join(search_items).strip()
                search_criteria = f"({search_text})"
                messages = self.session.search(None, search_criteria)[1][0]
                msg_ids.extend(messages.split())
                job.logger.debug(
                    f"Fetched {len(messages.split())} emails from {self.name}"
                    f" source using search pattern: {search_criteria}."
                )
        else:
            search_criteria = f"({since_date})"
            messages = self.session.search(None, search_criteria)[1][0]
            msg_ids.extend(messages.split())
            job.logger.debug(
                f"Fetched {len(messages.split())} emails from {self.name} "
                f"source using search pattern: {search_criteria}."
            )

        received_notifications = []
        for msg_id in msg_ids:
            raw_notification = self.fetch_email(job, msg_id)
            if raw_notification:
                received_notifications.append(raw_notification)

        job.logger.debug(f"Raw notifications created {len(received_notifications)} from {self.name}.")

        self.close_session()
        return received_notifications
