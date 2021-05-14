"""Init for Circuit Maintenance plugin."""
__version__ = "0.1.1"
from django.db.models.signals import post_migrate
from nautobot.extras.plugins import PluginConfig


def custom_field_extension(sender, **kwargs):  # pylint: disable=unused-argument
    """Add extended custom field."""
    # pylint: disable=import-outside-toplevel
    from django.contrib.contenttypes.models import ContentType
    from nautobot.circuits.models import Provider
    from nautobot.extras.choices import CustomFieldTypeChoices
    from nautobot.extras.models import CustomField

    for provider_cf_dict in [
        {
            "name": "emails_circuit_maintenances",
            "type": CustomFieldTypeChoices.TYPE_TEXT,
            "label": "Emails for Circuit Maintenance plugin",
        },
    ]:
        field, _ = CustomField.objects.get_or_create(name=provider_cf_dict["name"], defaults=provider_cf_dict)
        field.content_types.set([ContentType.objects.get_for_model(Provider)])


class CircuitMaintenanceConfig(PluginConfig):
    """Plugin configuration for the Circuit Maintenance plugin."""

    name = "nautobot_circuit_maintenance"
    verbose_name = "Circuit Maintenance"
    version = __version__
    author = "Network to Code, LLC"
    description = ""
    base_url = "circuit-maintenance"
    min_version = "1.0.0-beta.4"
    max_version = "1.999"
    required_settings = []
    default_settings = {}
    caching_config = {}

    def ready(self):
        super().ready()
        post_migrate.connect(custom_field_extension, sender=self)


config = CircuitMaintenanceConfig  # pylint:disable=invalid-name
