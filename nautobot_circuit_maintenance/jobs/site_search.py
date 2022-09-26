"""Site searching Job definition."""
import collections
from datetime import datetime, date
from django.conf import settings
from typing import NamedTuple

from django.contrib.contenttypes.models import ContentType
from nautobot.extras.jobs import Job
from nautobot.circuits.models import Circuit
from nautobot.dcim.models import Site
from nautobot.extras.models import Tag
from nautobot.utilities.choices import ColorChoices

from nautobot_circuit_maintenance.models import CircuitImpact, CircuitMaintenance

name = "Circuit Maintenance"  # pylint: disable=invalid-name
PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("nautobot_circuit_maintenance", {})
CIRCUIT_MAINTENANCE_TAG_COLOR = "Purple"


class Range(NamedTuple):
    start: datetime
    end: datetime


def check_for_overlap(record1: CircuitMaintenance, record2: CircuitMaintenance):
    # Build a couple of ranges
    range1 = Range(start=record1.start_time, end=record1.end_time)
    range2 = Range(start=record2.start_time, end=record2.end_time)

    # Determine the latest start and the earliest end to determine overlap
    latest_start = max(range1.start, range2.start)
    earliest_end = min(range1.end, range2.end)

    # Get the delta, compare versus 0 (negative number is no overlap)
    delta = (earliest_end - latest_start).days + 1

    # If delta is negative there is no overlap, return false
    overlap = max(0, delta)

    return overlap != 0


def get_sites_from_circuit(circuit: Circuit):
    """Get a list of sites from a circuit object in Nautobot.

    Args:
        circuit (Circuit): Nautobot Circuit Object to find the sites


    Returns:
        list: List of Nautobot Site objects
    """
    site_list: list = []
    for term in [circuit.termination_a, circuit.termination_z]:
        if term is not None and getattr(term, "provider_network") is None and term.site not in site_list:
            site_list.append(term.site)

    return site_list


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
                if term is not None:
                    return_dictionary[term.site.name].add(record)

    return dict(return_dictionary)


class FindSitesWithCircuitImpact(Job):
    """Nautobot Job definition for finding sites without redundant circuit for impactful maintenance.

    Args:
        Job (Nautobot Job): Nautobot Job import.
    """

    class Meta:
        """Meta definition for the Job."""

        name = "Find Sites With Circuit Impact"
        description = "Search for sites with multiple circuits, 1 or more circuit impacts."
        read_only = True

    def run(self, data=None, commit=None):
        """Executes the Job.

        Args:
            data (_type_, optional): _description_. Defaults to None.
            commit (_type_, optional): _description_. Defaults to None.
        """
        # Query for all of the circuits maintenances that are on going in the future
        today = date.today()
        circuit_maintenances = CircuitMaintenance.objects.filter(start_time__gte=today).order_by("start_time")

        # Query for all of the circuits within Nautobot
        all_circuits = Circuit.objects.all()
        circuit_maintenance_mapper = build_sites_to_maintenance_mapper(circuit_maintenances)

        # Loop over each of the circuit maintenance records
        for ckt_maint in circuit_maintenances:
            # Get the list of sites
            for circuit in ckt_maint.circuits:
                sites = get_sites_from_circuit(circuit)

            # Check to see if there are any circuit maintenances that are duplicated time
            for site in sites:
                for other_ckt_maint in circuit_maintenance_mapper[site.name]:
                    # Report failures for any time where a circuit will take an outage
                    if ckt_maint == other_ckt_maint:
                        self.log_info("Found each other!")
                        continue
                    if check_for_overlap(ckt_maint, other_ckt_maint):
                        self.log_warning(
                            obj=site,
                            message=f"There is an overlapping maintenance for site: {site.name}. Other maintenances: {other_ckt_maint}",
                        )
                    else:
                        # Log success for each time there is a known circuit still available at the site at the same time
                        self.log_success(
                            obj=ckt_maint, message="Checked maintenance for overlap, no overlap was found."
                        )
