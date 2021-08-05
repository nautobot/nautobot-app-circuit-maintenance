"""Custom Validators definition."""
from nautobot.circuits.models import Provider
from nautobot.extras.plugins import PluginCustomValidator
from nautobot.extras.models import CustomField

from circuit_maintenance_parser import SUPPORTED_PROVIDER_NAMES


class ProviderEmailValidator(PluginCustomValidator):
    """Custom validator to validate that Providers don't repeat source emails."""

    model = "circuits.provider"

    def clean(self):
        """Validate that provider emails are not repeated."""
        used_emails = []
        for provider in Provider.objects.all():
            if self.context["object"] != provider:
                for custom_field, value in provider.get_custom_fields().items():
                    if custom_field.name == "emails_circuit_maintenances" and value:
                        used_emails.extend(value.split(","))

        for custom_field, value in self.context["object"].get_custom_fields().items():
            if custom_field.name == "emails_circuit_maintenances" and value:
                for email in value.split(","):
                    if email in used_emails:
                        self.validation_error(
                            {"cf_emails_circuit_maintenances": f"{email} was already in used by another Provider."}
                        )


class ProviderParserValidator(PluginCustomValidator):
    """Custom validator to validate that Provider's parser exists in the Parser library."""

    model = "circuits.provider"

    def clean(self):
        """Validate that the Provider's parser exists in the Parser library."""
        provider_mapping = (
            self.context["object"]
            .get_custom_fields()
            .get(CustomField.objects.get(name="provider_parser_circuit_maintenances"))
        )

        if provider_mapping and provider_mapping.lower() not in SUPPORTED_PROVIDER_NAMES:
            self.validation_error(
                {
                    "cf_provider_parser_circuit_maintenances": (
                        f"{provider_mapping} is not one of the supported Providers in the "
                        f"circuit-maintenance-parser library: {SUPPORTED_PROVIDER_NAMES}."
                    )
                }
            )


custom_validators = [ProviderEmailValidator, ProviderParserValidator]
