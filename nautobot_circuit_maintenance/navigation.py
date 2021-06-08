"""Navigation for Circuit Maintenance."""
from nautobot.extras.plugins import PluginMenuButton, PluginMenuItem
from nautobot.utilities.choices import ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link="plugins:nautobot_circuit_maintenance:circuitmaintenance_list",
        link_text="Circuit Maintenances",
        permissions=["nautobot_circuit_maintenance.view_circuitmaintenance"],
        buttons=(
            PluginMenuButton(
                link="plugins:nautobot_circuit_maintenance:circuitmaintenance_add",
                title="List Circuit Maintenances",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["nautobot_circuit_maintenance.add_circuitmaintenance"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:nautobot_circuit_maintenance:rawnotification_list",
        link_text="Notifications",
        permissions=["nautobot_circuit_maintenance.view_circuitmaintenance"],
        buttons=(
            PluginMenuButton(
                link="plugins:nautobot_circuit_maintenance:notificationsource_list",
                title="Notification Sources",
                icon_class="mdi mdi-tune",
                color=ButtonColorChoices.YELLOW,
                permissions=["nautobot_circuit_maintenance.add_circuitmaintenance"],
            ),
        ),
    ),
)
