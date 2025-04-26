"""Gmail Sources."""

import base64
import datetime
import email
import logging
import time
from typing import Dict, Iterable, List, Optional, Union

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError
from nautobot.extras.jobs import Job

from nautobot_circuit_maintenance.enum import MessageProcessingStatus
from nautobot_circuit_maintenance.models import NotificationSource

from .base import MaintenanceNotification, RedirectAuthorize
from .email import EmailSource

logger = logging.getLogger(__name__)


class GmailAPI(EmailSource):
    """GmailAPI class."""

    credentials_file: str
    account: str
    service: Optional[Resource] = None
    credentials: Optional[Union[service_account.Credentials, Credentials]] = None

    # The required scope for baseline functionality (add gmail.modify permission in extra_scopes to enable tagging)
    SCOPES: List[str] = ["https://www.googleapis.com/auth/gmail.readonly"]

    extra_scopes: List[str] = []
    limit_emails_with_not_header_from: List[str] = []
    labels: Dict[str, str] = {}

    class Config:
        """Pydantic BaseModel config."""

        arbitrary_types_allowed = True

    def load_credentials(self, force_refresh=False):
        """Load Credentials for Gmail API."""
        raise NotImplementedError

    def build_service(self):
        """Build API service."""
        self.service = build("gmail", "v1", credentials=self.credentials)

    def close_service(self):
        """Close API Service."""
        if self.service:
            self.service.close()

    def _authentication_logic(self):
        """Inner method to run the custom class validation logic."""
        self.load_credentials(force_refresh=True)

    def extract_raw_payload(self, body: Dict, msg_id: str) -> bytes:
        """Extracts the raw_payload from body or attachement."""
        if "attachmentId" in body:
            attachment = (
                self.service.users()  # pylint: disable=no-member
                .messages()
                .attachments()
                .get(userId=self.account, messageId=msg_id, id=body["attachmentId"])
                .execute()
            )
            return base64.b64decode(attachment["data"])
        if "data" in body:
            return base64.urlsafe_b64decode(body["data"])

        return b""

    @staticmethod
    def _execute_with_retries(request, job, retries=5, delay=1, backoff=2):
        """
        Executes a Google API request with retries and exponential backoff.

        Args:
            request: The Google API request object.
            job: Job object to log.
            retries (int): Maximum number of retries.
            delay (int/float): Initial delay between retries.
            backoff (int/float): Backoff multiplier to increase delay.

        Returns:
            The result of the successful execution of the request.

        Raises:
            HttpError: If all retries fail, it raises the last HttpError.
        """
        attempt = 0
        last_response = None
        while attempt < retries:
            try:
                return request.execute()
            except HttpError as http_error:
                # Check if the error is retryable (e.g., 500, 503, rate limit)
                last_response = http_error.resp
                if http_error.resp.status in [500, 502, 503, 504]:
                    attempt += 1
                    job.logger.warning(
                        f"Google API attempt {attempt} failed: {http_error}. Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)
                    delay *= backoff
                else:
                    # Raise the error if it's not retryable (e.g., 400, 403)
                    raise

        if last_response:
            raise HttpError(resp=last_response, content=last_response.reason)
        return None

    def fetch_email(self, job: Job, msg_id: str) -> Optional[MaintenanceNotification]:
        """Fetch an specific email ID.

        See data format:  https://developers.google.com/gmail/api/reference/rest/v1/users.messages#Message
        """
        request = (
            self.service.users()  # pylint: disable=no-member
            .messages()
            .get(userId=self.account, id=msg_id, format="raw")
        )

        received_email = self._execute_with_retries(request, job)

        raw_email_string = base64.urlsafe_b64decode(received_email["raw"].encode("utf8"))
        email_message = email.message_from_bytes(raw_email_string)
        return self.process_email(job, email_message, msg_id)

    def _get_search_criteria(self, since_timestamp: datetime.datetime = None) -> str:
        """Build "search" criteria to filter emails, from date of from sender."""
        search_criteria = ""
        if since_timestamp:
            since_txt = since_timestamp.strftime("%Y/%m/%d")
            search_criteria = f"after:{since_txt}"

        # If source_header is not "From" but some other custom header such as X-Original-Sender,
        # the Gmail API doesn't let us filter by that, but if we provided via config a list of
        # source via `limit_emails_with_not_header_from`, we filter by that.
        if self.emails_to_fetch and self.source_header == "From":
            emails_with_from = [f"from:{email}" for email in self.emails_to_fetch]
            search_criteria += " {" + f'{" ".join(emails_with_from)}' + "}"
        elif self.emails_to_fetch and self.limit_emails_with_not_header_from:
            emails_with_from = [f"from:{email}" for email in self.limit_emails_with_not_header_from]
            search_criteria += " {" + f'{" ".join(emails_with_from)}' + "}"

        return search_criteria

    def tag_message(self, job: Job, msg_id: Union[str, bytes], tag: MessageProcessingStatus):
        """Apply the given Gmail label to the given message."""
        # Do we have a configured label ID corresponding to the given tag?
        if tag.value not in self.labels:
            return

        # Gmail API expects a str msg_id, but MaintenanceNotification coerces it to bytes - change it back if needed
        if isinstance(msg_id, bytes):
            msg_id = str(msg_id.decode())

        try:
            self.service.users().messages().modify(  # pylint: disable=no-member
                userId=self.account, id=msg_id, body={"addLabelIds": [self.labels[tag.value]]}
            ).execute()
        except HttpError:
            job.logger.warning(
                f"Error in applying tag '{tag.value}' ({self.labels[tag.value]}) to message {msg_id}:",
                exc_info=True,
            )

    def receive_notifications(
        self, job: Job, since_timestamp: datetime.datetime = None
    ) -> Iterable[MaintenanceNotification]:
        """Retrieve emails since an specific time, if provided."""
        self.load_credentials()
        self.build_service()

        search_criteria = self._get_search_criteria(since_timestamp)

        # messages.list() returns 100 emails at a time;
        # we need to loop with list_next() until we have all relevant messages
        request = (
            self.service.users().messages().list(userId=self.account, q=search_criteria)  # pylint: disable=no-member
        )
        msg_ids = []
        while request is not None:
            response = request.execute()
            msg_ids.extend(msg["id"] for msg in response.get("messages", []))
            request = self.service.users().messages().list_next(request, response)  # pylint: disable=no-member

        job.logger.debug(
            f"Fetched {len(msg_ids)} emails from {self.name} source using search pattern: {search_criteria}."
        )

        received_notifications = []
        for msg_id in msg_ids:
            raw_notification = self.fetch_email(job, msg_id)
            if raw_notification:
                received_notifications.append(raw_notification)

        job.logger.debug(f"Raw notifications created {len(received_notifications)} from {self.name}.")
        job.logger.debug(f"Raw notifications: {received_notifications}")

        self.close_service()
        return received_notifications


class GmailAPIOauth(GmailAPI):
    """GmailAPIOauth class.

    See: https://developers.google.com/identity/protocols/oauth2/web-server
    """

    def load_credentials(self, force_refresh=False):
        """Load Gmail API OAuth credentials."""
        notification_source = NotificationSource.objects.get(name=self.name)
        try:
            self.credentials = notification_source.token
        except EOFError:
            logger.debug("Google OAuth Token has not been initialized yet.")

        if force_refresh or not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.refresh_token and (self.credentials.expired or force_refresh):
                try:
                    self.credentials.refresh(Request())
                except RefreshError:
                    # Bad token, discard it
                    notification_source._token = b""  # pylint: disable=protected-access
                    notification_source.save()
                    raise

                notification_source.token = self.credentials
                notification_source.save()
            else:
                raise RedirectAuthorize(url_name="google_authorize", source_name=self.name)


class GmailAPIServiceAccount(GmailAPI):
    """GmailAPIServiceAccount class."""

    def load_credentials(self, force_refresh=False):
        """Load Gmail API Service Account credentials."""
        if force_refresh or not self.credentials:
            self.credentials = service_account.Credentials.from_service_account_file(self.credentials_file)
            self.credentials = self.credentials.with_scopes(self.SCOPES + self.extra_scopes)
            self.credentials = self.credentials.with_subject(self.account)
            self.credentials.refresh(Request())
