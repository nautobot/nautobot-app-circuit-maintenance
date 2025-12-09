"""Notification Source classes."""

import datetime
from typing import Iterable, Tuple, Union

from nautobot.extras.jobs import Job
from pydantic import BaseModel

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

    def validate_providers(self, job: Job, notification_source: NotificationSource, since_txt: str) -> bool:
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

    def tag_message(self, job: Job, msg_id: Union[str, bytes], tag: MessageProcessingStatus):
        """If supported, apply the given tag to the given message for future reference and categorization.

        The default implementation of this method is a no-op but specific Source subclasses may implement it.
        """


MaintenanceNotification.model_rebuild()
