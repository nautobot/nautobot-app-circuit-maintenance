"""Source module."""

from .base import Source
from .ews import ExchangeWebService
from .exceptions import RedirectAuthorize
from .factory import get_notifications, init_source
from .gmail import GmailAPIOauth, GmailAPIServiceAccount
from .imap import IMAP
from .maintenance_notification import MaintenanceNotification

__all__ = [
    "get_notifications",
    "init_source",
    "RedirectAuthorize",
    "Source",
    "MaintenanceNotification",
    "ExchangeWebService",
    "IMAP",
    "GmailAPIOauth",
    "GmailAPIServiceAccount",
]
