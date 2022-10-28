"""Site searching Job definition."""
import collections
from datetime import datetime, date
from typing import NamedTuple

from django.conf import settings

from nautobot.extras.jobs import Job
from nautobot.circuits.models import Circuit

from nautobot_circuit_maintenance.models import CircuitMaintenance

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("nautobot_circuit_maintenance", {})
CIRCUIT_MAINTENANCE_TAG_COLOR = "Purple"

name = "Circuit Maintenance"  # pylint: disable=invalid-name


class DateTimeRange(NamedTuple):
    """Range class for use within the check for overlap.

    Args:
        NamedTuple (NamedTupe): Parent class
    """

    start: datetime
    end: datetime


def check_for_overlap(record1: CircuitMaintenance, record2: CircuitMaintenance):
    """Checks for the overlap of two circuit maintenance records.

    Args:
        record1 (CircuitMaintenance): First maintenance record
        record2 (CircuitMaintenance): Second maintenance record

    Returns:
        bool: Result of there is overlap
    """
    # Build a couple of ranges
    range1 = DateTimeRange(start=record1.start_time, end=record1.end_time)
    range2 = DateTimeRange(start=record2.start_time, end=record2.end_time)

    # Determine the latest start and the earliest end to determine overlap
    latest_start = max(range1.start, range2.start)
    earliest_end = min(range1.end, range2.end)

    # Get the delta, compare versus 0 (negative number is no overlap)
    delta = (earliest_end - latest_start).days + 1

    # If delta is negative there is no overlap, return false
    return delta > 0


def get_sites_from_circuit(circuit: Circuit):
    """Get a list of sites from a circuit object in Nautobot.

    Args:
        circuit (Circuit): Nautobot Circuit Object to find the sites


    Returns:
        list: List of Nautobot Site objects
    """
    site_set: set = set()
    for term in [circuit.termination_a, circuit.termination_z]:
        if term is not None and getattr(term, "provider_network") is None:
            site_set.add(term.site)

    return list(site_set)


def build_sites_to_maintenance_mapper(maintenance_queryset):
    """Build a site to circuit maintenance mapper so the data can be quickly accessed of what possible overlaps.

    Leverages defaultdict to provide the default value of an empty set to each key that will be added. Then adds each
    particular circuit maintenance object to the dictionary to be used as a map of maintenances going on at the site.
    Build a data dictionary that maps sites to circuit maintenances:

    data_dict = {
        "msp": {
            CM1,
            CM2
        },
        "nyc": {
            CM3,
            CM4
        }
    }

    Args:
        maintenance_queryset (Queryset): Queryset of all Circuit Maintenance objects

    Returns:
        dict: Dictionary of a set of maintenance records
    """
    return_dictionary = collections.defaultdict(set)
    for record in maintenance_queryset:
        # Get the site overall
        # Start with looping over the circuits that are defined
        for circuit in record.circuits:
            # Check both termination A and Z for values of None, add that record to the set for each site
            for term in [circuit.termination_a, circuit.termination_z]:
                # If the circuit is connected to a provider network, then it will return None for a site.
                # Also only checks connected circuits.
                if term.site is not None:
                    return_dictionary[term.site.name].add(record)

    return dict(return_dictionary)


class FindSitesWithMaintenanceOverlap(Job):
    """Nautobot Job definition for finding sites without redundant circuit for impactful maintenance.

    Current iteration of this job assumes that many sites will be only dual carrier connected. The searches are going
    to search for a single overlap in this first iteration.

    Future iterations may include the ability to search for multiple circuit overlaps that would allow for just a single
    circuit to be available.

    Args:
        Job (Nautobot Job): Nautobot Job parent class
    """

    class Meta:
        """Meta definition for the Job."""

        name = "Find Sites With Circuit Maintenance Overlap"
        description = "Search for sites with overlapping circuit maintenances, 1 or more circuit impacts, assuming only TWO circuits per site."

    def run(self, data=None, commit=None):
        """Executes the Job.

        Args:
            data (_type_, optional): _description_. Defaults to None.
            commit (_type_, optional): _description_. Defaults to None.
        """
        # Query for all of the circuits maintenances that are on going in the future
        today = date.today()
        circuit_maintenances = CircuitMaintenance.objects.filter(start_time__gte=today).order_by("start_time")

        # Build a circuit mapper
        circuit_maintenance_mapper = build_sites_to_maintenance_mapper(circuit_maintenances)

        # Loop over each of the circuit maintenance records
        # pylint: disable=too-many-nested-blocks
        counter: int = 0
        for circuit_maint in circuit_maintenances:
            counter += 1
            # Get the list of sites
            site_list: list = []
            for circuit in circuit_maint.circuits:
                site_list += get_sites_from_circuit(circuit)

            # Check to see if there are any circuit maintenances that are overlapping at some moment in time
            for site in site_list:
                for other_circuit_maint in circuit_maintenance_mapper[site.name]:
                    # Report failures for any time where a circuit will take an outage
                    if circuit_maint == other_circuit_maint:
                        continue
                    if check_for_overlap(circuit_maint, other_circuit_maint):
                        if PLUGIN_SETTINGS.get("overlap_job_exclude_no_impact"):
                            for impact in circuit_maint.circuitimpact_set:
                                if impact.impact != "NO-IMPACT":
                                    self.log_warning(
                                        obj=site,
                                        message=f"There is an overlapping maintenance for site: {site.name} on {circuit_maint.start_time}. Other maintenances: {other_circuit_maint}|{circuit_maint}",
                                    )
                        else:
                            self.log_warning(
                                obj=site,
                                message=f"There is an overlapping maintenance for site: {site.name} on {circuit_maint.start_time}. Other maintenances: {other_circuit_maint}|{circuit_maint}",
                            )
                    else:
                        # Log success for each time there is a known circuit still available at the site at the same time
                        self.log_debug(message="Checked maintenance for overlap, no overlap was found.")

        self.log_success(
            obj=None,
            message=f"Successfully checked through {counter} maintenance notification{'s' if counter > 1 else ''}.",
        )
