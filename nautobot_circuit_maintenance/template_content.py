"""Additions to existing Nautobot page content."""

from nautobot.apps.ui import TemplateExtension

from .models import CircuitImpact


# pylint: disable=abstract-method
class CircuitMaintenanceContent(TemplateExtension):
    """Add circuit information to the Device view."""

    model = "circuits.circuit"

    def right_page(self):
        """Show table on right side of view."""
        circuitimpacts = CircuitImpact.objects.filter(circuit__cid=self.context["object"].cid)[:5]
        return self.render(
            "nautobot_circuit_maintenance/circuit_extension.html", extra_context={"circuitimpacts": circuitimpacts}
        )


template_extensions = [CircuitMaintenanceContent]
