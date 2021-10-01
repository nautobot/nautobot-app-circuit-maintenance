"""Models for Circuit Maintenance."""
import pickle  # nosec
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver

from nautobot.extras.utils import extras_features
from nautobot.circuits.models import Circuit, Provider
from nautobot.core.models.generics import PrimaryModel, OrganizationalModel

from .choices import CircuitImpactChoices, CircuitMaintenanceStatusChoices, NoteLevelChoices

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("nautobot_circuit_maintenance", {})
DEFAULT_RAW_NOTIFICATION_SIZE = 1000


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    # "graphql",  # TODO: https://github.com/nautobot/nautobot/issues/399
    "relationships",
    "statuses",
    "webhooks",
)
class CircuitMaintenance(PrimaryModel):
    """Model for circuit maintenances."""

    name = models.CharField(max_length=100, default="", unique=True, blank=False)
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
    # "graphql",  # TODO: https://github.com/nautobot/nautobot/issues/399
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
        return f"Circuit {self.circuit} with impact {self.impact}"

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
    title = models.TextField()
    level = models.CharField(
        default=NoteLevelChoices.INFO,
        max_length=50,
        choices=NoteLevelChoices,
        null=True,
        blank=True,
    )
    comment = models.TextField()
    date = models.DateTimeField(default=now)

    csv_headers = ["maintenance", "title", "level", "comment"]

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        ordering = ["date"]
        unique_together = ["maintenance", "title"]

    def __str__(self):
        """String value for HTML rendering."""
        return f"{self.title}"

    def get_absolute_url(self):
        """Returns reverse loop up URL."""
        return reverse("plugins:nautobot_circuit_maintenance:note", args=[self.pk])

    def to_csv(self):
        """Return fields for bulk view."""
        return (self.maintenance, self.title, self.level, self.comment, self.date)


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

    raw = models.BinaryField()
    subject = models.CharField(max_length=200)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, default=None)
    sender = models.CharField(max_length=200, default="", null=True, blank=True)
    source = models.ForeignKey(NotificationSource, on_delete=models.SET_NULL, null=True)
    parsed = models.BooleanField(default=False, null=True, blank=True)
    # RawNotification.date is the date when the RawNotification was received by the Source
    date = models.DateTimeField(default=now)

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        ordering = ["date"]
        unique_together = ("date", "provider", "subject")

    def save(self, *args, **kwargs):
        """Custom save for RawNotification."""
        # Limiting the size of the notification stored.
        self.raw = self.raw[
            : PLUGIN_SETTINGS.get("raw_notifications", {}).get("raw_notification_size", DEFAULT_RAW_NOTIFICATION_SIZE)
        ]
        super().save(*args, **kwargs)

    def __str__(self):
        """String value for HTML rendering."""
        return f"{self.subject}"

    def get_absolute_url(self):
        """Returns reverse loop up URL."""
        return reverse("plugins:nautobot_circuit_maintenance:rawnotification", args=[self.pk])

    def to_csv(self):
        """Return fields for bulk view."""
        return (self.subject, self.provider, self.sender, self.source, self.raw, self.date, self.parsed)


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
    # ParsedNotification.date is the date when after parsing a RawNotification, the ParsedNotification was created
    date = models.DateTimeField(default=now)

    class Meta:  # noqa: D106 "Missing docstring in public nested class"
        ordering = ["date"]

    def __str__(self):
        """String value for HTML rendering."""
        return f"Parsed notification for {self.raw_notification.subject}"

    def get_absolute_url(self):
        """Returns reverse loop up URL."""
        return reverse("plugins:nautobot_circuit_maintenance:parsednotification", args=[self.pk])

    def to_csv(self):
        """Return fields for bulk view."""
        return (self.maintenance, self.raw_notification, self.json, self.date)
