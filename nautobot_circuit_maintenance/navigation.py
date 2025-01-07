"""Menu items."""

from nautobot.apps.ui import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab

items = (
    NavMenuItem(
        link="plugins:nautobot_circuit_maintenance:circuitmaintenance_list",
        name="Circuit Maintenance",
        permissions=["nautobot_circuit_maintenance.view_circuitmaintenance"],
        buttons=(
            NavMenuAddButton(
                link="plugins:nautobot_circuit_maintenance:circuitmaintenance_add",
                permissions=["nautobot_circuit_maintenance.add_circuitmaintenance"],
            ),
        ),
    ),
)

menu_items = (
    NavMenuTab(
        name="Apps",
        groups=(NavMenuGroup(name="Circuit Maintenance", items=tuple(items)),),
    ),
)
