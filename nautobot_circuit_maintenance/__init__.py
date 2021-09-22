"""Init for Circuit Maintenance plugin."""
try:
    from importlib import metadata
except ImportError:
    # Python version < 3.8
    import importlib_metadata as metadata

__version__ = metadata.version(__name__)

from django.conf import settings
from django.db.models.signals import post_migrate
from django.utils.text import slugify
from nautobot.extras.plugins import PluginConfig


def custom_fields_extension(sender, **kwargs):  # pylint: disable=unused-argument
    """Add extended custom fields."""
    # pylint: disable=import-outside-toplevel
    from django.contrib.contenttypes.models import ContentType
    from nautobot.circuits.models import Provider
    from nautobot.extras.choices import CustomFieldTypeChoices
    from nautobot.extras.models import CustomField

    for provider_cf_dict in [
        {
            "name": "emails_circuit_maintenances",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "Emails for Circuit Maintenance plugin.",
        },
        {
            "name": "provider_parser_circuit_maintenances",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "Provider Parser for Circuit Maintenance plugin.",
        },
    ]:
        field, _ = CustomField.objects.get_or_create(name=provider_cf_dict["name"], defaults=provider_cf_dict)
        field.content_types.set([ContentType.objects.get_for_model(Provider)])


def import_notification_sources(sender, **kwargs):  # pylint: disable=unused-argument
    """Import Notification Sources from Nautobot_configuration.py.

    This is a temporary solution until a secrets backend is implemented.
    For now, we create the Notification Sources in the DB but the secrets are fetched via ENV.
    """
    # pylint: disable=import-outside-toplevel
    from nautobot.circuits.models import Provider
    from nautobot_circuit_maintenance.models import NotificationSource

    desired_notification_sources_names = []
    for notification_source in settings.PLUGINS_CONFIG.get("nautobot_circuit_maintenance", {}).get(
        "notification_sources", []
    ):
        instance, _ = NotificationSource.objects.update_or_create(
            name=notification_source["name"],
            slug=slugify(
                notification_source["name"],
            ),
            defaults={
                "attach_all_providers": notification_source.get("attach_all_providers", False),
            },
        )

        desired_notification_sources_names.append(notification_source["name"])

        if instance.attach_all_providers:
            for provider in Provider.objects.all():
                instance.providers.add(provider)

    # We remove old Notification Sources that could be in Nautobot but removed from configuration
    NotificationSource.objects.exclude(name__in=desired_notification_sources_names).delete()


class CircuitMaintenanceConfig(PluginConfig):
    """Plugin configuration for the Circuit Maintenance plugin."""

    name = "nautobot_circuit_maintenance"
    verbose_name = "Circuit Maintenance"
    version = __version__
    author = "Network to Code, LLC"
    author_email = "opensource@networktocode.com"
    description = "Automatically handle network circuit maintenance notifications."
    base_url = "circuit-maintenance"
    min_version = "1.0.0-beta.4"
    max_version = "1.999"
    required_settings = []
    default_settings = {}
    caching_config = {}

    def ready(self):
        super().ready()
        post_migrate.connect(custom_fields_extension, sender=self)
        post_migrate.connect(import_notification_sources, sender=self)

        # App metrics are disabled by default
        if settings.PLUGINS_CONFIG.get("nautobot_circuit_maintenance", {}).get("metrics", {}).get("enable", False):
            # pylint: disable=import-outside-toplevel
            from nautobot_capacity_metrics import register_metric_func
            from .metrics_app import metric_circuit_operational

            register_metric_func(metric_circuit_operational)


config = CircuitMaintenanceConfig  # pylint:disable=invalid-name
