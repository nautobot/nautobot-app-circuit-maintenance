"""Navigation for Circuit Maintenance."""

from nautobot.utilities.choices import ButtonColorChoices
from nautobot.core.apps import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab, NavMenuButton

# For Nautobot 1.5.8, once that becomes the minimum:
# from nautobot.apps.ui import (NavMenuTab, NavMenuGroup, NavMenuItem, NavMenuButton)

menu_items = (
    NavMenuTab(
        name="Circuits",
        groups=(
            NavMenuGroup(
                name="Circuit Maintenance App",
                weight=250,
                items=(
                    NavMenuItem(
                        link="plugins:nautobot_circuit_maintenance:circuitmaintenance_overview",
                        name="Dashboard",
                        permissions=["nautobot_circuit_maintenance.view_circuitmaintenance"],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_circuit_maintenance:circuitmaintenance_list",
                        name="Circuit Maintenances",
                        permissions=["nautobot_circuit_maintenance.view_circuitmaintenance"],
                        buttons=(
                            NavMenuAddButton(
                                link="plugins:nautobot_circuit_maintenance:circuitmaintenance_add",
                                title="Add Circuit Maintenance",
                                permissions=["nautobot_circuit_maintenance.add_circuitmaintenance"],
                            ),
                            NavMenuButton(
                                link="plugins:nautobot_circuit_maintenance:circuitmaintenance_job",
                                title="Job to update Circuit Maintenance",
                                icon_class="mdi mdi-language-python",
                                button_class=ButtonColorChoices.BLUE,
                                permissions=["nautobot_circuit_maintenance.add_circuitmaintenance"],
                            ),
                        ),
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_circuit_maintenance:rawnotification_list",
                        name="Notifications",
                        permissions=["nautobot_circuit_maintenance.view_circuitmaintenance"],
                    ),
                    NavMenuItem(
                        link="plugins:nautobot_circuit_maintenance:notificationsource_list",
                        name="Notification Sources",
                        permissions=["nautobot_circuit_maintenance.view_notificationsource"],
                    ),
                ),
            ),
        ),
    ),
)
