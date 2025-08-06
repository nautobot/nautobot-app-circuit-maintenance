"""Manteinance Notification Models."""

from typing import TYPE_CHECKING
from pydantic import BaseModel


if TYPE_CHECKING:
    from nautobot_circuit_maintenance.handle_notifications.sources.base import Source


class MaintenanceNotification(BaseModel):
    """Representation of all the data related to a Maintenance Notification."""

    msg_id: bytes
    source: "Source"
    sender: str
    subject: str
    provider_type: str
    raw_payload: bytes
    date: str
