"""Create fixtures for tests."""

from nautobot_circuit_maintenance.models import CircuitMaintenance


def create_circuitmaintenance():
    """Fixture to create necessary number of CircuitMaintenance for tests."""
    CircuitMaintenance.objects.create(name="Test One")
    CircuitMaintenance.objects.create(name="Test Two")
    CircuitMaintenance.objects.create(name="Test Three")
