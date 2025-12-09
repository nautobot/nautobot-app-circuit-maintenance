"""Navigation for Circuit Maintenance."""

from nautobot.apps.ui import (
    NavigationIconChoices,
    NavigationWeightChoices,
    NavMenuGroup,
    NavMenuItem,
    NavMenuTab,
)

menu_items = (
    NavMenuTab(
        name="Circuits",
        icon=NavigationIconChoices.CIRCUITS,
        weight=NavigationWeightChoices.CIRCUITS,
        groups=(
            NavMenuGroup(
                name="Circuit Maintenance App",
                weight=250,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_circuit_maintenance:circuitmaintenance_overview",
                        name="Dashboard",
                        weight=100,
                        permissions=["nautobot_circuit_maintenance.view_circuitmaintenance"],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_circuit_maintenance:circuitmaintenance_list",
                        name="Circuit Maintenances",
                        weight=200,
                        permissions=["nautobot_circuit_maintenance.view_circuitmaintenance"],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_circuit_maintenance:rawnotification_list",
                        name="Notifications",
                        weight=300,
                        permissions=["nautobot_circuit_maintenance.view_circuitmaintenance"],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_circuit_maintenance:notificationsource_list",
                        name="Notification Sources",
                        weight=400,
                        permissions=["nautobot_circuit_maintenance.view_notificationsource"],
                    ),
                ),
            ),
        ),
    ),
)
