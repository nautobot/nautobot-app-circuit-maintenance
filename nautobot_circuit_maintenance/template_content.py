"""Additions to existing Nautobot page content."""
from nautobot.extras.plugins import PluginTemplateExtension
from .models import CircuitImpact


# pylint: disable=abstract-method
class CircuitMaintenanceContent(PluginTemplateExtension):
    """Add circuit information to the Device view."""

    model = "circuits.circuit"

    def right_page(self):
        """Show table on right side of view."""
        circuitimpacts = CircuitImpact.objects.filter(circuit__cid=self.context["object"].cid)[:5]
        return self.render(
            "nautobot_circuit_maintenance/circuit_extension.html", extra_context={"circuitimpacts": circuitimpacts}
        )


template_extensions = [CircuitMaintenanceContent]
