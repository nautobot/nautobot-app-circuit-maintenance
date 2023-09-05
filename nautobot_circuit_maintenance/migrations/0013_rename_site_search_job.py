from django.db import migrations


def _rename_site_to_location(apps, _schema_editor):
    Job = apps.get_model("extras", "Job")

    # Rename the field
    Job.objects.filter(job_class_name="FindSitesWithMaintenanceOverlap").update(
        job_class_name="FindLocationsWithMaintenanceOverlap",
        name="Find Locations With Circuit Maintenance Overlap",
        module_name="nautobot_circuit_maintenance.jobs.location_search",
        description="Search for locations with overlapping circuit maintenances, 1 or more circuit impacts, assuming only TWO circuits per location.",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_circuit_maintenance", "0012_auto_20230810_1245"),
    ]

    operations = [
        migrations.RunPython(_rename_site_to_location),
    ]
