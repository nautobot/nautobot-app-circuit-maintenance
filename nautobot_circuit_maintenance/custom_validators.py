"""Custom Validators definition."""
from nautobot.circuits.models import Provider
from nautobot.extras.plugins import PluginCustomValidator


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


custom_validators = [ProviderEmailValidator]
