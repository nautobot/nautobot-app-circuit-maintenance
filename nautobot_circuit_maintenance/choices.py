"""ChoiceSet classes for circuit maintenance."""

from nautobot.utilities.choices import ChoiceSet

# See: https://github.com/jda/maintnote-std/blob/master/standard.md


class CircuitMaintenanceStatusChoices(ChoiceSet):
    """Valid values for Circuit Maintenance Status.

    See: https://github.com/jda/maintnote-std/blob/master/standard.md
    """

    TENTATIVE = "TENTATIVE"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    IN_PROCESS = "IN-PROCESS"
    COMPLETED = "COMPLETED"
    RE_SCHEDULED = "RE-SCHEDULED"

    UNKNOWN = "UNKNOWN"

    CHOICES = (
        (TENTATIVE, "TENTATIVE"),
        (CONFIRMED, "CONFIRMED"),
        (CANCELLED, "CANCELLED"),
        (IN_PROCESS, "IN-PROCESS"),
        (COMPLETED, "COMPLETED"),
        (RE_SCHEDULED, "RE-SCHEDULED"),
        (UNKNOWN, "UNKNOWN"),
    )


class CircuitImpactChoices(ChoiceSet):
    """Valid values for Circuit Maintenance Impact.

    See: https://github.com/jda/maintnote-std/blob/master/standard.md
    """

    NO_IMPACT = "NO-IMPACT"
    REDUCED_REDUNDANCY = "REDUCED-REDUNDANCY"
    DEGRADED = "DEGRADED"
    OUTAGE = "OUTAGE"

    CHOICES = (
        (NO_IMPACT, "NO-IMPACT"),
        (REDUCED_REDUNDANCY, "REDUCED-REDUNDANCY"),
        (DEGRADED, "DEGRADED"),
        (OUTAGE, "OUTAGE"),
    )


class NoteLevelChoices(ChoiceSet):
    """Valid values for Circuit Maintenance Note level."""

    INFO = "INFO"
    WARNING = "WARNING"

    CHOICES = (
        (INFO, "INFO"),
        (WARNING, "WARNING"),
    )
