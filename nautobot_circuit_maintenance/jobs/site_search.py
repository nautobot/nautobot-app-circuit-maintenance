"""Site searching Job definition."""

import collections
from datetime import date

from django.conf import settings

from nautobot.extras.jobs import BooleanVar, Job
from nautobot.circuits.models import Circuit

from nautobot_circuit_maintenance.models import CircuitMaintenance

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("nautobot_circuit_maintenance", {})
CIRCUIT_MAINTENANCE_TAG_COLOR = "Purple"

name = "Circuit Maintenance"  # pylint: disable=invalid-name


def check_for_overlap(record1: CircuitMaintenance, record2: CircuitMaintenance) -> bool:
    """Checks for the overlap of two circuit maintenance records.

    Args:
        record1 (CircuitMaintenance): First maintenance record
        record2 (CircuitMaintenance): Second maintenance record

    Returns:
        bool: True if there is overlap, otherwise False.
    """
    if record1.end_time < record2.start_time or record2.end_time < record1.start_time:
        return False

    return True


def get_sites_from_circuit(circuit: Circuit) -> set:
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

    return site_set


def build_sites_to_maintenance_mapper(maintenance_queryset) -> dict:
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
                if term is not None and term.site is not None:
                    return_dictionary[term.site.name].add(record)

    return dict(return_dictionary)


class FindSitesWithMaintenanceOverlap(Job):
    """Nautobot Job definition for finding sites without redundant circuit for impactful maintenance.

    Current iteration of this job assumes that many sites will be only dual carrier connected. The searches are going
    to search for a single overlap in this first iteration.

    Future iterations may include the ability to search for multiple circuit overlaps that would allow for just a single
    circuit to be available.
    """

    job_debug = BooleanVar(description="Enable for more verbose debug logging")

    class Meta:
        """Meta definition for the Job."""

        name = "Find Sites With Circuit Maintenance Overlap"
        description = "Search for sites with overlapping circuit maintenances, 1 or more circuit impacts, assuming only TWO circuits per site."

    def run(self, data=None, commit=None):
        """Executes the Job.

        Args:
            data (dict, optional): Data from Nautobot from. Defaults to None.
            commit (bool, optional): Commit boolean. Defaults to None.
        """
        # Query for all of the circuits maintenances that are on going in the future
        today = date.today()
        circuit_maintenances = CircuitMaintenance.objects.filter(start_time__gte=today).order_by("start_time")

        # Build a circuit mapper
        circuit_maintenance_mapper = build_sites_to_maintenance_mapper(circuit_maintenances)

        # Loop over each of the circuit maintenance records
        # pylint: disable=too-many-nested-blocks
        processed_maintenance_list = []  # List of the processed maintenance records
        for circuit_maint in circuit_maintenances:
            # Get the set of sites
            site_set: set = set()
            for circuit in circuit_maint.circuits:
                site_set.update(get_sites_from_circuit(circuit))

            processed_maintenance_list.append(circuit_maint)
            overlapping_maintenance = False  # Flag for overlapping maintenance present
            # Check to see if there are any circuit maintenances that are overlapping at some moment in time
            for site in site_set:
                for other_circuit_maint in circuit_maintenance_mapper[site.name]:
                    # Report failures for any time where a circuit will take an outage
                    # Check to see if the other circuit maintenance has already had overlap checked.
                    # If this is the same circuit maintenance record, that will also show up in the processed list
                    # since the list is being added to before the loop.
                    if other_circuit_maint in processed_maintenance_list:
                        continue
                    if check_for_overlap(circuit_maint, other_circuit_maint):
                        overlapping_maintenance = True
                        if PLUGIN_SETTINGS.get("overlap_job_exclude_no_impact"):
                            for circuit_impact in circuit_maint.circuitimpact_set:
                                if circuit_impact.impact != "NO-IMPACT":
                                    break
                            else:
                                continue

                        self.log_warning(
                            obj=site,
                            message=f"There is an overlapping maintenance for site: {site.name} on {circuit_maint.start_time}. Other maintenances: {other_circuit_maint}|{circuit_maint}",
                        )

            # Log success for when there is not an overlapping maintenance at a site
            if overlapping_maintenance is False and data["job_debug"]:
                self.log_info(obj=circuit_maint, message="Checked maintenance for overlap, no overlap was found.")

        self.log_success(
            obj=None,
            message=f"Successfully checked through {circuit_maintenances.count()} maintenance notification{'s'[:circuit_maintenances.count()^1]}.",
        )
