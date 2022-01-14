"""Models for Circuit Maintenance."""
import logging
import pickle  # nosec
from datetime import datetime, timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

from nautobot.extras.utils import extras_features
from nautobot.circuits.models import Circuit, Provider
from nautobot.core.models.generics import PrimaryModel, OrganizationalModel

from .choices import CircuitImpactChoices, CircuitMaintenanceStatusChoices, NoteLevelChoices

logger = logging.getLogger(__name__)

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("nautobot_circuit_maintenance", {})

MAX_MAINTENANCE_NAME_LENGTH = 100
MAX_NOTIFICATION_SENDER_LENGTH = 200
MAX_NOTIFICATION_SUBJECT_LENGTH = 200
MAX_NOTIFICATION_TOTAL_LENGTH = 16384
MAX_NOTE_TITLE_LENGTH = 200


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "statuses",
    "webhooks",
)
class CircuitMaintenance(PrimaryModel):
    """Model for circuit maintenances."""

    name = models.CharField(max_length=MAX_MAINTENANCE_NAME_LENGTH, default="", unique=True, blank=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(null=True, blank=True)
    # TODO: Status could use the new general Status model
    status = models.CharField(
        default=CircuitMaintenanceStatusChoices.TENTATIVE,
        max_length=50,
        choices=CircuitMaintenanceStatusChoices,
        null=True,
        blank=True,
    )
    ack = models.BooleanField(default=False, null=True, blank=True)

    csv_headers = ["name", "start_time", "end_time", "description", "status", "ack"]

    @property
    def circuits(self):
        """Queryset of Circuit records associated with this CircuitMaintenance."""
        return Circuit.objects.filter(circuitimpact__maintenance=self)

    @property
    def providers(self):
        """Queryset of Provider records associated with this CircuitMaintenance."""
        return Provider.objects.filter(circuits__circuitimpact__maintenance=self)

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        ordering = ["start_time"]

    def __str__(self):
        """String value for HTML rendering."""
        return f"{self.name}"

    def get_absolute_url(self):
        """Returns reverse loop up URL."""
        return reverse("plugins:nautobot_circuit_maintenance:circuitmaintenance", args=[self.pk])

    def clean(self):
        """Add validation when creating a Circuit Maintenance.

        Todo:
            - Status state machine
        """
        super().clean()

        if self.end_time < self.start_time:
            raise ValidationError("End time should be greater than start time.")

    def to_csv(self):
        """Return fields for bulk view."""
        return (self.name, self.start_time, self.end_time, self.description, self.status, self.ack)


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class CircuitImpact(OrganizationalModel):
    """Model for Circuit Impact."""

    maintenance = models.ForeignKey(CircuitMaintenance, on_delete=models.CASCADE)
    circuit = models.ForeignKey(Circuit, on_delete=models.CASCADE)
    impact = models.CharField(
        default=CircuitImpactChoices.OUTAGE,
        max_length=50,
        choices=CircuitImpactChoices,
        null=True,
        blank=True,
    )

    csv_headers = ["maintenance", "circuit", "impact"]

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        ordering = ["maintenance", "impact"]
        unique_together = ["maintenance", "circuit"]

    def __str__(self):
        """String value for HTML rendering."""
        # str(self) is used in change logging, and ObjectChange.object_repr field is limited to 200 characters.
        return f"Circuit {self.circuit} with impact {self.impact}"[:200]

    def get_absolute_url(self):
        """Returns reverse loop up URL."""
        return reverse("plugins:nautobot_circuit_maintenance:circuitimpact", args=[self.pk])

    def to_csv(self):
        """Return fields for bulk view."""
        return (self.maintenance, self.circuit, self.impact)


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "relationships",
    "webhooks",
)
class Note(OrganizationalModel):
    """Model for maintenance notes."""

    maintenance = models.ForeignKey(CircuitMaintenance, on_delete=models.CASCADE, default=None)
    title = models.CharField(max_length=MAX_NOTE_TITLE_LENGTH)
    level = models.CharField(
        default=NoteLevelChoices.INFO,
        max_length=50,
        choices=NoteLevelChoices,
        null=True,
        blank=True,
    )
    comment = models.TextField()

    csv_headers = ["maintenance", "title", "level", "comment"]

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        ordering = ["last_updated"]
        unique_together = ["maintenance", "title"]

    def __str__(self):
        """String value for HTML rendering."""
        # str(self) is used in change logging, and ObjectChange.object_repr field is limited to 200 characters.
        return f"{self.title}"[:200]

    def get_absolute_url(self):
        """Returns reverse loop up URL."""
        return reverse("plugins:nautobot_circuit_maintenance:note", args=[self.pk])

    def to_csv(self):
        """Return fields for bulk view."""
        return (self.maintenance, self.title, self.level, self.comment, self.last_updated)


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "relationships",
    "webhooks",
)
class NotificationSource(OrganizationalModel):
    """Model for Notification Source configuration."""

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Notification Source Name as defined in configuration file.",
    )
    slug = models.SlugField(max_length=100, unique=True)
    providers = models.ManyToManyField(
        Provider,
        help_text="The Provider(s) that this Notification Source applies to.",
        blank=True,
    )
    _token = models.BinaryField(
        blank=True,
    )
    attach_all_providers = models.BooleanField(
        default=False,
        help_text="Attach all the Providers to this Notification Source",
    )

    csv_headers = ["name", "slug", "providers"]

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        ordering = ["name"]

    def __str__(self):
        """String value for HTML rendering."""
        return f"{self.name}"

    def get_absolute_url(self):
        """Returns reverse loop up URL."""
        return reverse("plugins:nautobot_circuit_maintenance:notificationsource", args=[self.slug])

    def to_csv(self):
        """Return fields for bulk view."""
        return (self.name, self.slug, self.providers)

    @property
    def token(self):
        """Getter for _token."""
        return pickle.loads(self._token)  # nosec

    @token.setter
    def token(self, value):
        """Setter for _token."""
        self._token = pickle.dumps(value)


@receiver(post_save, sender=Provider)
def add_provider_to_email_sources(sender, instance, created, **kwargs):  # pylint: disable=unused-argument
    """Listen to Provider's creation to add them to the NotificationSources that have the attach_all_providers flag."""
    if created:
        for notification_source in NotificationSource.objects.filter(attach_all_providers=True):
            notification_source.providers.add(instance)


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "relationships",
    "webhooks",
)
class RawNotification(OrganizationalModel):
    """Model for maintenance notifications in raw format."""

    raw = models.BinaryField(max_length=MAX_NOTIFICATION_TOTAL_LENGTH)
    subject = models.CharField(max_length=MAX_NOTIFICATION_SUBJECT_LENGTH)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, default=None)
    sender = models.CharField(max_length=MAX_NOTIFICATION_SENDER_LENGTH, default="", null=True, blank=True)
    source = models.ForeignKey(NotificationSource, on_delete=models.SET_NULL, null=True)
    parsed = models.BooleanField(default=False, null=True, blank=True)
    # RawNotification.stamp is the date when the RawNotification was received by the Source
    stamp = models.DateTimeField()

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        ordering = ["stamp"]
        unique_together = ("stamp", "provider", "subject")

    def save(self, *args, **kwargs):
        """Custom save for RawNotification."""
        # Limiting the size of the notification stored.
        notification_length = min(PLUGIN_SETTINGS.get("raw_notification_size"), MAX_NOTIFICATION_TOTAL_LENGTH)
        self.raw = self.raw[:notification_length]
        super().save(*args, **kwargs)

    def __str__(self):
        """String value for HTML rendering."""
        return f"{self.subject}"

    def get_absolute_url(self):
        """Returns reverse loop up URL."""
        return reverse("plugins:nautobot_circuit_maintenance:rawnotification", args=[self.pk])

    def to_csv(self):
        """Return fields for bulk view."""
        return (self.subject, self.provider, self.sender, self.source, self.raw, self.stamp, self.parsed)

    def clean(self):
        """Add validation when creating a RawNotification."""
        super().clean()

        if self.stamp > datetime.now(timezone.utc):
            logger.warning("Stamp time %s is not consistent, it's in the future.", self.stamp)


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "relationships",
    "webhooks",
)
class ParsedNotification(OrganizationalModel):
    """Model for maintenance notifications after parsing."""

    maintenance = models.ForeignKey(CircuitMaintenance, on_delete=models.CASCADE, default=None)
    raw_notification = models.ForeignKey(RawNotification, on_delete=models.CASCADE, default=None)
    json = models.JSONField()

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        ordering = ["last_updated"]

    def __str__(self):
        """String value for HTML rendering."""
        # str(self) is used in change logging, and ObjectChange.object_repr field is limited to 200 characters.
        return f"Parsed notification for {self.raw_notification.subject}"[:200]

    def get_absolute_url(self):
        """Returns reverse loop up URL."""
        return reverse("plugins:nautobot_circuit_maintenance:parsednotification", args=[self.pk])

    def to_csv(self):
        """Return fields for bulk view."""
        return (self.maintenance, self.raw_notification, self.json, self.last_updated)
